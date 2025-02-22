# SPDX-License-Identifier: BSD-3-Clause
# This code was yoinked from https://github.com/usb-tools/ViewSB and
# adapted to add features,

import math
import string
import enum

from PySide2.QtCore    import *
from PySide2.QtGui     import *
from PySide2.QtWidgets import *


@enum.unique
class ByteFormat(enum.Enum):
	base16 = enum.auto()
	base10 = enum.auto()
	base08 = enum.auto()
	base02 = enum.auto()

	def __str__(self):
		if self == ByteFormat.base16:
			return 'Hexadecimal'
		elif self == ByteFormat.base10:
			return 'Decimal'
		elif self == ByteFormat.base08:
			return 'Octal'
		elif self == ByteFormat.base02:
			return 'Binary'
		else:
			return '?'

	@staticmethod
	def from_str(s):
		if s == 'Decimal':
			return ByteFormat.base10
		elif s == 'Octal':
			return ByteFormat.base08
		elif s == 'Binary':
			return ByteFormat.base02
		else:
			return ByteFormat.base16

	def __float__(self):
		if self == ByteFormat.base16:
			return 1.0
		elif self == ByteFormat.base02:
			return 4.0
		else:
			return 1.5

class HexViewWidget(QTableView):

	def _to_corresponding_column(self, column):
		""" Returns the ASCII or hex column for the corresponding hex or ASCII column respectively. """

		bytes_per_row = self.model().columnCount() // 2

		if column < bytes_per_row:
			return column + bytes_per_row + 1
		else:
			return column - (bytes_per_row + 1)

	def _set_bytes_per_row(self, bytes_per_row):
		""" Sets up column count and column widths for the selected bytes-per-row (either 8 or 16). """

		assert bytes_per_row in (8, 16)

		# Hex columns, ASCII columns, and one separator column.
		column_count = bytes_per_row * 2 + 1
		self.model().setColumnCount(column_count)

		# Set column width for the hex columns, which each contain two characters.
		for column in range(bytes_per_row):
			self.setColumnWidth(column, self.hex_width * float(self.byteFormat))

		# Set the column width for the separator column.
		self.setColumnWidth(bytes_per_row, self.ascii_width * 2)

		# Set the column width for the ASCII columns, which each contain one character.
		for column in range(bytes_per_row + 1, column_count):
			self.setColumnWidth(column, self.ascii_width)


	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		# Properties
		self.showControlGlyphs = True
		self.font = QFont('Fira Code', 12)
		self.byteFormat = ByteFormat.base16
		self.colorMap = {
			'zero'     : QColor('#494A50'),
			'low'      : QColor('#00994D'),
			'high'     : QColor('#CD427E'),
			'ones'     : QColor('#6C2DBE'),
			'printable': QColor('#FFB45B')
		}

		self.setShowGrid(False)
		self.horizontalHeader().hide()
		self.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
		self.verticalHeader().setHighlightSections(False)
		self.horizontalHeader().setHighlightSections(False)
		self.verticalHeader().setSectionsClickable(False)

		# Don't let the user edit the table cells.
		self.setEditTriggers(self.NoEditTriggers)

		self.setSelectionBehavior(QAbstractItemView.SelectItems)
		self.setSelectionMode(QAbstractItemView.ContiguousSelection)

		self.setModel(QStandardItemModel(1, 33))

		# This will store the raw data that is displayed in the hex view.
		self.hex_data = None

		# Determine how wide ASCII columns should be.
		self.ascii_width = self.fontMetrics().horizontalAdvance('m')

		# HACK: Get how much space a hex item needs by asking temporarily creating one, and then asking Qt,
		# because self.fontMetrics().width('mm') isn't enough, apparently, unlike above.
		self.model().setItem(0, 0, QStandardItem('mm'))
		self.resizeColumnToContents(0)
		self.hex_width = self.visualRect(self.model().createIndex(0, 0)).width()

		# Default to 16 hex columns, with 16 ASCII columns, and one separator column, for a total of 33.
		self._set_bytes_per_row(16)

		# HACK: Get how much space is needed for 16 bytes per row by
		# getting the left and right bound of the left-most and right-most items, respectively.
		start = self.visualRect(self.model().createIndex(0, 0)).left()
		end = self.visualRect(self.model().createIndex(0, 32)).right()
		self.full_width = end - start

		# Record the default background color for items, since apparently that's platform dependent.
		# Note: Normally we can only get the default background color if there's actually an item there,
		# but we made one earlier to determine the value for self.hex_width, so we don't need to do it again.
		self.default_background_color = self.model().item(0, 0).background()

		self.model().setRowCount(0)

		self.selectionModel().selectionChanged.connect(self._selection_changed)

	def setSelection(self, rect, flags):
		""" Overrides QTableView.setSelection().

		Qt Tables force multi-cell selections to be grid like, but we want this to act like a
		text box for selection purposes. That is to say that we want selections to wrap around.
		Since Qt doesn't have any setting that lets us do that, we have to subclass QTableView
		and reimplement setSelection.
		"""

		def is_index_enabled(index):
			""" Reimplementation of the Qt private inline function of the same name."""
			return self.model().flags(index) & Qt.ItemIsEnabled


		#
		# Partial reimplementation of the original function.
		#

		tl = self.indexAt(QPoint(max(rect.left(), rect.right()) if self.isRightToLeft()
			else min(rect.left(), rect.right()), min(rect.top(), rect.bottom())))
		br = self.indexAt(QPoint(min(rect.left(), rect.right()) if self.isRightToLeft()
			else max(rect.left(), rect.right()), max(rect.top(), rect.bottom())))

		if (not self.selectionModel) or (not tl.isValid()) or (not br.isValid()) or \
				(not is_index_enabled(tl)) or (not is_index_enabled(br)):
			return


		#
		# My code follows.
		#

		bytes_per_row = self.model().columnCount() // 2

		# Don't let the user touch or cross the separator.
		if tl.column() <= bytes_per_row <= br.column():
			return

		# Don't let the user select empty items.
		# Note: There's a reason we're using item() instead of itemFromIndex(), which is that
		# itemFromIndex() will lazily create an item at that index if there isn't one,
		# and we explicitly want to check if there is an item or not.
		if self.model().item(tl.row(), tl.column()) is None or \
				self.model().item(br.row(), br.column()) is None:
			return


		selection = QItemSelection()

		selection_range = QItemSelectionRange(tl, br)
		if not selection_range.isEmpty():

			# Add this range, and then my custom range.
			selection.append(selection_range)

			# If we have a multi-line selection.
			if tl.row() < br.row():

				# If the selection is on the hex side...
				if br.column() < bytes_per_row:

					# ...each line will be limited to first and last hex item of that row.
					left_min = 0
					right_max = bytes_per_row - 1

				# If the selection is on the ASCII side...
				else:

					# ...each line will be limited to the first and last ASCII item of that row.
					left_min = bytes_per_row + 1
					right_max = bytes_per_row * 2

				# Select the rest of each row except the bottom row.
				for row in range(tl.row(), br.row()):

					left_index = self.model().createIndex(row, tl.column())
					right_index = self.model().createIndex(row, right_max)
					selection.append(QItemSelectionRange(left_index, right_index))


				# Select the beginning for each row except the top row.
				for row in range(tl.row() + 1, br.row() + 1):

					left_index = self.model().createIndex(row, left_min)
					right_index = self.model().createIndex(row, br.column())
					selection.append(QItemSelectionRange(left_index, right_index))


		self.selectionModel().select(selection, flags)

	@property
	def showControlGlyphs(self):
		return self._show_ctl_glyph

	@showControlGlyphs.setter
	def showControlGlyphs(self, val):
		self._show_ctl_glyph = val

	@property
	def font(self):
		return self._font

	@font.setter
	def font(self, val):
		self._font = val
		self._font.setStyleHint(QFont.Monospace)
		self.setFont(self._font)

	@property
	def byteFormat(self):
		return self._byte_format

	@byteFormat.setter
	def byteFormat(self, val):
		self._byte_format = val



	def resizeEvent(self, event):
		""" Overrides QAbstractItemView.resizeEvent().

		This swaps the hexview between full mode and half mode based on what will fit.
		Full mode shows 16 hex items and 16 ASCII items per row.
		Half mode shows 8 hex items and 8 ASCII items per row.
		"""

		super().resizeEvent(event)


		# If there's nothing in the hexview right now, we don't care.
		if self.model().rowCount() == 0:
			return


		# If we have enough room for full mode...
		if event.size().width() > self.full_width:

			# and we're not already in full mode...
			if self.model().columnCount() != 33:

				# change to full mode...
				self._set_bytes_per_row(16)

				# and re-fill out the table.
				self.populate(self.hex_data)

		# If we _don't_ have enough room for full mode...
		else:

			# and we're not already in half mode...
			if self.model().columnCount() != 17:

				# change to half mode...
				self._set_bytes_per_row(8)

				# and re-fill out the table.
				self.populate(self.hex_data)


	def _selection_changed(self, _selected, deselected):
		"""
		Handler for the QTableView.selectionChanged() signal that highlights the ASCII or hex items that
		correspond to the hex or ASCII items the user selected, respectively.
		"""

		# First, un-highlight the items that correspond to the ones that were deselected.
		for index in deselected.indexes():

			# Note: We're not using itemFromIndex() because it behaves slightly differently, and
			# under this setup it sometimes returns None.
			deselected_item = self.model().item(index.row(), index.column())

			other_item = self.model().item(deselected_item.row(),
				self._to_corresponding_column(deselected_item.column()))

			# This can happen if e.g. the corresponding column was removed entirely
			# by switching to half mode.
			if other_item is not None:
				other_item.setBackground(self.default_background_color)


		# Now, highlight the items that correspond to the ones that are currently selected.
		currently_selected_indexes = self.selectionModel().selectedIndexes()

		for index in currently_selected_indexes:

			# Highlight the corresponding other item.
			other_item = self.model().item(index.row(),
				self._to_corresponding_column(index.column()))
			other_item.setBackground(QColor('#AF92FB'))

	def _classifyByte(self, byte):
		if byte == 0x00:
			return self.colorMap['zero']
		elif byte == 0xFF:
			return self.colorMap['ones']
		elif byte <= 0x20:
			return self.colorMap['low']
		elif byte >= 0x7F:
			return self.colorMap['high']
		else:
			return self.colorMap['printable']


	def populate(self, raw_data):
		""" Populate the hex and ASCII items.

		Args:
			raw_data -- bytes object containing the raw binary data to be displayed.
		"""

		def row_column_enumerate(iterable):
			""" Turns the index into row-column coordinates suitable for a hexview."""
			for index, value in enumerate(iterable):
				yield divmod(index, self.model().columnCount() // 2), value


		self.hex_data = raw_data

		model = self.model()

		# Reset.
		# Note: We're not using clear() as that would also clear e.g. column settings.
		model.setRowCount(0)

		# Calculate how many rows we need.
		bytes_per_row = model.columnCount() // 2
		data_len = len(raw_data)
		needed_rows = math.ceil(data_len / bytes_per_row)

		model.setRowCount(needed_rows)

		format_specifier = '{:02X}'
		if self.byteFormat == ByteFormat.base10:
			format_specifier = '{:03d}'
		elif self.byteFormat == ByteFormat.base08:
			format_specifier = '{:03o}'
		elif self.byteFormat == ByteFormat.base02:
			format_specifier = '{:08b}'


		address_labels = ['{:04X}'.format(i) for i in range(0, data_len, bytes_per_row)]
		model.setVerticalHeaderLabels(address_labels)

		for (row, col), byte in row_column_enumerate(raw_data):
			colour = QBrush(self._classifyByte(byte))

			hex_item = QStandardItem(format_specifier.format(byte))
			hex_item.setForeground(colour)
			char = chr(byte)

			if byte <= 32 and self.showControlGlyphs:
				ascii_item = QStandardItem(chr(byte + 0x2400))
			elif char in string.printable:
				ascii_item = QStandardItem(char)
			else:
				ascii_item = QStandardItem('·')

			ascii_item.setForeground(colour)

			model.setItem(row, col, hex_item)
			model.setItem(row, self._to_corresponding_column(col), ascii_item)


if __name__ == '__main__':
	import sys

	class MainWindow(QMainWindow):
		def __init__(self):
			super().__init__()

			self.resize(1024, 768)

			self.container = QFrame()
			self.layout = QVBoxLayout()

			self._widget = HexViewWidget()

			self.layout.addWidget(self._widget, Qt.AlignCenter, Qt.AlignCenter)

			self.container.setLayout(self.layout)
			self.setCentralWidget(self._widget)

	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()

	with open('/usr/bin/echo', 'rb') as f:
		mw._widget.populate(f.read())

	sys.exit(app.exec_())
