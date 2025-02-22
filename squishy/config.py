# SPDX-License-Identifier: BSD-3-Clause

from pathlib import Path
from os      import environ
import enum

SQUISHY_NAME = 'squishy'

# XDG directories
XDG_HOME        = Path.home()                 if 'XDG_HOME'        not in environ else Path(environ['XDG_HOME'])
XDG_CACHE_DIR   = (XDG_HOME / '.cache')       if 'XDG_CACHE_HOME'  not in environ else Path(environ['XDG_CACHE_HOME'])
XDG_DATA_HOME   = (XDG_HOME / '.local/share') if 'XDG_DATA_HOME'   not in environ else Path(environ['XDG_DATA_HOME'])
XDG_CONFIG_HOME = (XDG_HOME / '.config')      if 'XDG_CONFIG_HOME' not in environ else Path(environ['XDG_CONFIG_HOME'])

# Squishy-specific sub dirs
SQUISHY_CACHE   = (XDG_CACHE_DIR   / SQUISHY_NAME)
SQUISHY_DATA    = (XDG_DATA_HOME   / SQUISHY_NAME)
SQUISHY_CONFIG  = (XDG_CONFIG_HOME / SQUISHY_NAME)

SQUISHY_APPLETS      = (SQUISHY_DATA  / 'applets')
SQUISHY_APPLET_CACHE = (SQUISHY_CACHE / 'applets')

SQUISHY_BUILD_DIR    = (SQUISHY_CACHE / 'build')

# File path constants
SQUISHY_SETTINGS_FILE = (SQUISHY_CONFIG / 'settings.json')
SQUISHY_HISTORY_FILE  = (SQUISHY_CACHE  / '.repl-history')

# Some cute/funny splash messages
SQUISHY_SPLASH_MESSAGES = [
	'moe moe kyun~',
	'SCSI - Soft Catgirl Snuggles Interface',
	'Antifascist Action',
	':nya_hearts:',
	'fpga cat people love brushies - it’s comb logic',
	'are there lots of cat girl programmers because they enjoy hunting bugs?',
	'no gods, no masters, only catgirls',
	'when in doubt, snuggle blåhaj',
	'*smol nya*',
	'ITAR export-restricted catgirl',
	'catgirl go *squimsh*',
	'tape go nyooooooooooooooooooom',
	'*slow blink*',
	'Sachi is a good foxgirl',
	'bappy pawbs',
	'Trans rights are human rights',
]

# Defaults
DEFAULT_SETTINGS = {
	'gui': {
		'appearance': {
			'show_splash'    : True,
			'theme'          : 'system',
			'language'       : 'en_US',
			'font': {
				'name': 'Noto Sans',
				'size': 12,
			},

			'toolbar_style': 'Icons Only',

			'hex_view': {
				'byte_format': 'Hexadecimal',
				'font': {
					'name': 'Fira Code',
					'size': 12
				},

				'color_map': {
					'zero'     : '#494A50',
					'low'      : '#00994D',
					'high'     : '#CD427E',
					'ones'     : '#6C2DBE',
					'printable': '#FFB45B',
				}
			}
		},
		'hotkeys': {
			'Menu': {
				'File': {
					'action_file_new_session': 'Ctrl+N',
					'action_file_open'       : 'Ctrl+O',
					'action_file_save'       : 'Ctrl+S',
					'action_file_save_as'    : 'Ctrl+Shift+S',
					'action_file_export_as'  : 'Ctrl+Shift+X',
					'action_file_quit'       : 'Ctrl+Q',
				},
				'Edit': {
					'Copy As...': {
						'action_copy_binary'   : '',
						'action_copy_hex'      : '',
						'action_copy_c_array'  : '',
						'action_copy_cpp_array': '',
						'action_copy_json'     : '',
					},
					'action_edit_find'         : 'Ctrl+F',
					'action_edit_find_next'    : 'Ctrl+Shift+N',
					'action_edit_find_previous': 'Ctrl+Shift+B',
					'action_edit_chrono_shift' : 'Ctrl+Shift+T',
					'action_edit_preferences'  : 'Ctrl+Shift+P',
				},
				'View': {
					'action_view_hex'         : '',
					'action_view_dissector'   : '',
					'action_view_repl'        : '',
					'action_view_toolbar'     : '',
					'action_view_bus_topology': '',
				},
				'Go': {
					'action_go_message' : 'Ctrl+G',
					'action_go_previous': 'Ctrl+Down',
					'action_go_next'    : 'Ctrl+Up',
					'action_go_first'   : 'Ctrl+Home',
					'action_go_last'    : 'Ctrl+End',
				},
				'Capture': {
					'action_capture_start'        : 'Ctrl+E',
					'action_capture_stop'         : 'Ctrl+Shift+E',
					'action_capture_restart'      : 'Ctrl+R',
					'action_capture_replay'       : 'Ctrl+Shift+R',
					'action_capture_filters'      : '',
					'action_capture_triggers'     : '',
					'action_capture_select_device': 'Ctrl+D',
					'action_capture_auto_scroll'  : '',
				},
				'Help': {
					'action_help_website': '',
					'action_help_about'  : '',
				}
			}
		},
	},
	'capture': {
		'buffer': {
			'size'   : 4096,
			'type'   : 'Ring Buffer',
			'backend': 'mmap',
		},
	},
	'device': {

	},

}

# Various enums that don't have a home yet
@enum.unique
class BufferType(enum.Enum):
	Ring       = enum.auto()
	Contiguous = enum.auto()

	def __str__(self) -> str:
		if self == BufferType.Ring:
			return 'Ring Buffer'
		elif self == BufferType.Contiguous:
			return 'Contiguous'
		else:
			return '?'

	@staticmethod
	def from_str(s : str):
		if s == 'Contiguous':
			return BufferType.Contiguous
		else:
			return BufferType.Ring


@enum.unique
class BufferBackend(enum.Enum):
	mmap     = enum.auto()
	file     = enum.auto()
	bytes_io = enum.auto()

	def __str__(self) -> str:
		if self == BufferBackend.mmap:
			return 'mmap'
		elif self == BufferBackend.file:
			return 'File'
		elif self == BufferBackend.bytes_io:
			return 'BytesIO'
		else:
			return '?'

	@staticmethod
	def from_str(s : str):
		if s == 'File':
			return BufferBackend.file
		elif s == 'BytesIO':
			return BufferBackend.bytes_io
		else:
			return BufferBackend.mmap

# Hardware Metadata, etc
USB_VID             = 0x1209
USB_PID_BOOTLOADER  = 0xCA71
USB_PID_APPLICATION = 0xCA70
USB_MANUFACTURER    = 'Shrine Maiden Heavy Industries'
USB_PRODUCT         = {
	USB_PID_BOOTLOADER : 'Squishy Bootloader',
	USB_PID_APPLICATION: 'Squishy',
}
# This is the temporary serial number
USB_SERIAL_NUMBER   = 'ニャ〜'

SCSI_VID            = 'Shrine-0'
