# SPDX-License-Identifier: BSD-3-Clause

from .. import SquishyApplet

class Analyzer(SquishyApplet):
	preview       = True
	pretty_name   = 'SCSI Analyzer'
	description   = 'SCSI Bus analyzer and replay'
	short_help    = description
	hardware_rev  = (
		'rev1', 'rev2'
	)
	supports_gui  = True
	supports_repl = True

	def init_gui(self, main_window, args):
		pass

	def init_repl(self, repl_ctx, args):
		pass

	def build(self, interfaces, platform, args):
		pass

	def register_args(self, parser):
		pass

	def init_applet(self, args):
		pass

	def run(self, device, args):
		pass
