# SPDX-License-Identifier: BSD-3-Clause

from os import path, environ

SQUISHY_NAME = 'squishy'

XDG_CACHE_DIR   = path.join(path.expanduser('~'), '.cache') if 'XDG_CACHE_HOME' not in environ else environ['XDG_CACHE_HOME']
XDG_DATA_HOME   = path.join(path.expanduser('~'), '.local/share') if 'XDG_DATA_HOME' not in environ else environ['XDG_DATA_HOME']
XDG_CONFIG_HOME = path.join(path.expanduser('~'), '.config') if 'XDG_CONFIG_HOME' not in environ else environ['XDG_CONFIG_HOME']

SQUISHY_CACHE   = path.join(XDG_CACHE_DIR, SQUISHY_NAME)
SQUISHY_DATA    = path.join(XDG_DATA_HOME, SQUISHY_NAME)
SQUISHY_CONFIG  = path.join(XDG_CONFIG_HOME, SQUISHY_NAME)

SQUISHY_APPLETS = path.join(SQUISHY_DATA, 'applets')
