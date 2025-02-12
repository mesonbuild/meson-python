# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import sys


_path = os.path.join(os.path.dirname(__file__), '..', '.link_against_local_lib.mesonpy.libs')
if os.name == 'nt':
    os.add_dll_directory(_path)
elif sys.platform == 'cygwin':
    os.environ['PATH'] = os.pathsep.join((os.environ['PATH'], _path))
del _path


from ._example import example_sum  # noqa: E402


__all__ = ['example_sum']
