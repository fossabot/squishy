# SPDX-License-Identifier: BSD-3-Clause

import logging as log
from pathlib            import Path

from amaranth.build.run import LocalBuildProducts

from .config            import SQUISHY_APPLET_CACHE

__all__ = (
	'SquishyBitstreamCache',
)

class SquishyBitstreamCache:
	# Initialize the cache directory
	def _init_cache_dir(self, root, depth = 1):
		if depth == 0:
			return

		for i in range(256):
			cache_stub = root / f'{i:02x}'
			if not cache_stub.exists():
				cache_stub.mkdir()
				self._init_cache_dir(cache_stub, depth - 1)

	def _decompose_digest(self, digest):
		return [
			digest[
				(i*2):((i*2)+2)
			]
			for i in range(len(digest) // 2)
		]

	def _get_cache_dir(self, digest):
		return self._cache_root.joinpath(
			*self._decompose_digest(digest)[
				:self.tree_depth
			]
		)

	def __init__(self, do_init = True, tree_depth = 1):
		self.tree_depth  = tree_depth
		self._cache_root = Path(SQUISHY_APPLET_CACHE)

		if do_init:
			if not (self._cache_root / 'ca').exists():
				log.debug(f'Initializing bitstream cache tree')
				self._init_cache_dir(self._cache_root, tree_depth)

	def flush(self):
		log.info('Flushing applet cache')
		self._cache_root.rmdir()
		self._cache_root.mkdir()


	def get(self, digest):
		bitstream_name = f'{digest}.bin'
		cache_dir = self._get_cache_dir(digest)
		bitstream = cache_dir / bitstream_name

		log.debug(f'Looking up bitstream \'{bitstream_name}\' in \'{cache_dir}\'')

		if not bitstream.exists():
			log.debug(f'Bitstream not found in cache')
			return None

		log.info(f'Using cached bitstream \'{bitstream}\'')

		return {
			'name'    : bitstream_name,
			'products': LocalBuildProducts(str(cache_dir))
		}

	def store(self, digest, products, name):
		bitstream_name = f'{digest}.bin'
		cache_dir = self._get_cache_dir(digest)
		bitstream = cache_dir / bitstream_name

		log.debug(f'Caching bitstream \'{name}\' in \'{cache_dir}\'')
		log.debug(f'New bitstream name: \'{bitstream_name}\'')

		with open(bitstream, 'wb') as bit:
			bit.write(products.get(f'{name}.bin'))
