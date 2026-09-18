# SPDX-FileCopyrightText: 2024 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import sys


# start-literalinclude
def _append_to_sharedlib_load_path():
    """Ensure the shared libraries in this package can be loaded on Windows.

    Windows lacks a concept equivalent to RPATH: Python extension modules
    cannot find DLLs installed outside the DLL search path. This function
    ensures that the location of the shared libraries distributed inside this
    Python package is in the DLL search path of the process.

    The Windows DLL search path includes the path to the object attempting
    to load the DLL: it needs to be augmented only when the Python extension
    modules and the DLLs they require are installed in separate directories.
    Cygwin does not have the same default library search path: all locations
    where the shared libraries are installed need to be added to the search
    path.

    This function is very similar to the snippet inserted into the main
    ``__init__.py`` of a package by ``delvewheel`` when it vendors external
    shared libraries.

    .. note::

        `os.add_dll_directory` is only available for Python 3.8 and later, and
        in the Conda ``python`` packages it works as advertised only for
        version 3.10 and later. For older Python versions, pre-loading the DLLs
        with `ctypes.WinDLL` may be preferred.
    """
    basedir = os.path.dirname(__file__)
    subdir = os.path.join(basedir, 'sub')
    if os.name == 'nt':
        os.add_dll_directory(subdir)
    elif sys.platform == 'cygwin':
        os.environ['PATH'] = os.pathsep.join((os.environ['PATH'], basedir, subdir))


_append_to_sharedlib_load_path()
# end-literalinclude


from ._example import example_prod, example_sum  #noqa: E402


__all__ = ['example_prod', 'example_sum']
