.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _projects-using-meson-python:

********
Examples
********

The following project use ``meson-python`` for their build system known to be
adhering to best practices


:`SciPy <https://github.com/scipy/scipy>`_: Probably the most complex
   project using Meson and ``meson-python``.  It combines CPython
   extensions and libraries written in C, C++, Fortran, Cython_, and
   Pythran_.

:`scikit-image <https://github.com/scikit-image/scikit-image>`_:
   Another complex project using ``meson-python``.

:`siphash24 <https://github.com/dnicolodi/python-siphash24>`_: A very
   simple project. It demonstrates how Meson makes it trivial to
   compile a CPython extension written in `Cython`_ via a simple
   template engine and link it to a library compiled from a Meson
   subproject. Also an example of how to use `cibuildwheel`_ to
   produce Python wheels for several platforms.


.. _Cython: https://github.com/cython/cython
.. _Pythran: https://github.com/serge-sans-paille/pythran
.. _cibuildwheel: https://github.com/pypa/cibuildwheel
