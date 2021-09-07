# SPDX-License-Identifier: BSD-3-Clause
from nmigen                  import *
from nmigen_soc.wishbone     import Interface
from nmigen_soc.csr.bus      import Element, Multiplexer
from nmigen_soc.csr.wishbone import WishboneCSRBridge

__all__ = (
	'SCSIInterface',
)

# SCSI: Small Catgirl Scritches Interface
class SCSIInterface(Elaboratable):
	def __init__(self, *, config, wb_config):
		self.config = config
		self._scsi_id = Signal(8)


		self._wb_cfg = wb_config

		self.ctl_bus = Interface(
			addr_width  = self._wb_cfg['addr'],
			data_width  = self._wb_cfg['data'],
			granularity = self._wb_cfg['gran'],
			features    = self._wb_cfg['feat']
		)

		self._csr = {
			'mux'     : None,
			'elements': {}
		}
		self._init_csrs()
		self._csr_bridge = WishboneCSRBridge(self._csr['mux'].bus)
		self.bus = self._csr_bridge.wb_bus

		self.rx     = None
		self.tx     = None
		self.tx_ctl = None

		self._scsi_in_fifo = None
		self._usb_out_fifo = None

		self._status_led = None

	def connect_fifo(self, *, scsi_in, usb_out):
		if not len(scsi_in) == 4 or not len(usb_out) == 4:
			raise ValueError(f'expected a tuple of four signals for scsi_in and usb_out, got {scsi_in}, {usb_out}')

		self._scsi_in_fifo = scsi_in
		self._usb_out_fifo = usb_out

	def _init_csrs(self):
		self._csr['regs'] = {
			'status': Element(8, 'r')
		}

		self._csr['mux'] = Multiplexer(
			addr_width = 1,
			data_width = self._wb_cfg['data']
		)

		self._csr['mux'].add(self._csr['regs']['status'], addr = 0)

	def _csr_elab(self, m):
		m.d.comb += [
			self._csr['regs']['status'].r_data.eq(self._interface_status)
		]

	def elaborate(self, platform):
		# rx/tx data[0:8] = 0, 1, 2, 3, 4, 5, 6, 7, P
		self.rx     = platform.request('scsi_rx')
		self.tx     = platform.request('scsi_tx')
		self.tx_ctl = platform.request('scsi_tx_ctl')
		self._status_led = platform.request('led', 1)

		self._interface_status = Signal(8)

		m = Module()
		m.submodules += self._csr_bridge
		m.submodules.csr_mux = self._csr['mux']

		self._csr_elab(m)

		m.d.comb += [
			self._interface_status[0:6].eq(~self.tx_ctl)
		]

		# SCSI Bus timings:
		# 	min arbitration delay  - 2.2us
		# 	min assertion period   - 90ns
		# 	min bus clear delay    - 800ns
		# 	max bus clear delay    - 1.2us
		# 	min bus free delay     - 800ns
		# 	max bus set delay      - 1.8us
		# 	min bus settle delay   - 400ns
		# 	max cable skew delay   - 10ns
		# 	max data release delay - 400ns
		# 	min deskew delay       - 45ns
		# 	min hold time          - 45ns
		# 	min negation period    - 90ns
		# 	min reset hold time    - 25us
		# 	max sel abort time     - 200us
		# 	min sel timeout delay  - 250ms (recommended)
		with m.FSM(reset = 'rst'):
			with m.State('rst'):

				m.next = 'rst'
			# bus_free - no scsi device is using the bus
			#
			with m.State('bus_free'):
				# All signals are left high-z due to no target/initiator
				m.d.sync += [
					self.tx_ctl.eq(0b111111),
					self.tx.eq(0),
				]


				m.next = 'bus_free'

			with m.State('selection'):




				m.next = 'bus_free'

			with m.State('command'):



				m.next = 'bus_free'

			with m.State('data_in'):




				m.next = 'bus_free'

			with m.State('data_out'):



				m.next = 'bus_free'

			with m.State('message_in'):



				m.next = 'bus_free'

			with m.State('message_out'):



				m.next = 'bus_free'

			with m.State('status'):


				m.next = 'bus_free'

		return m

