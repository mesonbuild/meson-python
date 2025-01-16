# SPDX-FileCopyrightText: 2024 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import sys


# start-literalinclude
def _enable_sharedlib_loading():
    """
    Ensure the shared libraries in this dir and the ``sub`` subdir can be
    loaded on Windows.

    One shared library is installed alongside this ``__init__.py`` file.
    Windows can load it because it searches for DLLs in the directory where a
    ``.pyd`` (Python extension module) is located in. Cygwin does not though.
    For a shared library in another directory inside the package, Windows also
    needs a hint.

    This function is Windows-specific due to lack of RPATH support on Windows.
    It cannot find shared libraries installed within wheels unless we either
    amend the DLL search path or pre-load the DLL.

    Note that ``delvewheel`` inserts a similar snippet into the main
    ``__init__.py`` of a package when it vendors external shared libraries.

    .. note::

        `os.add_dll_directory` is only available for Python >=3.8, and with
        the Conda ``python`` packages only works as advertised for >=3.10.
        If you require support for older versions, pre-loading the DLL
        with `ctypes.WinDLL` may be preferred (the SciPy code base has an
        example of this).
    """
    basedir = os.path.dirname(__file__)
    subdir = os.path.join(basedir, 'sub')
    if os.name == 'nt':
        os.add_dll_directory(subdir)
    elif sys.platform == 'cygwin':
        os.environ['PATH'] = f'os.environ["PATH"]:{basedir}:{subdir}'


_enable_sharedlib_loading()
# end-literalinclude


from ._example import example_prod, example_sum  #noqa: E402


__all__ = ['example_prod', 'example_sum']
