#!/usr/bin/env python2
# Copyright 2019 The Emscripten Authors.  All rights reserved.
# Emscripten is available under two separate licenses, the MIT license and the
# University of Illinois/NCSA Open Source License.  Both these licenses can be
# found in the LICENSE file.

"""Update 'symbols' files based on the contents of libraries in the cache.
"""

import glob
import os
import sys

root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)

from tools import cache, shared

# Set this to True to apply the filtering to all existing files rather than
# reading symbols from the cached libraries
filter_in_place = False


def filter_and_sort(symbols):
  lines = symbols.splitlines()
  lines = [l.rstrip() for l in lines]
  lines = [l for l in lines if l and l[-1] != ':']
  # Remove local data and text symbols
  lines = [l for l in lines if ' d ' not in l]
  lines = [l for l in lines if ' t ' not in l]
  lines.sort(key=lambda x: x.split()[-1])
  return '\n'.join(lines) + '\n'


def main():
  cache_dir = cache.Cache().dirname

  symbols_dir = os.path.join(root_dir, 'system', 'lib')
  for symbol_file in glob.glob(os.path.join(symbols_dir, '*.symbols')):
    if filter_in_place:
      output = open(symbol_file).read()
    else:
      basename = os.path.splitext(os.path.basename(symbol_file))[0]
      if not basename.startswith('lib'):
        basename = 'lib' + basename
      basename = basename.replace('cxx', 'c++')
      pattern = os.path.join(cache_dir, basename + '.*')
      libs = glob.glob(pattern)
      if not libs:
        continue
      assert len(libs) == 1
      output = shared.run_process([shared.LLVM_NM, libs[0]], stdout=shared.PIPE).stdout
    new_symbols = filter_and_sort(output)

    with open(symbol_file, 'w') as f:
      f.write(new_symbols)

  return 0


if __name__ == '__main__':
  sys.exit(main())
