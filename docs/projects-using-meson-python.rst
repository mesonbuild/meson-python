.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _projects-using-meson-python:

********
Examples
********

Here's a curated list of projects using ``meson-python``.


.. list-table::
   :widths: 20 80

   * - `SciPy <https://github.com/scipy/scipy>`_
     - Probably the most complex project using Meson and ``meson-python``.
       It combines `CPython extensions`_ and libraries written in C, C++,
       Cython_, Fortran_, Pythran_, etc., it targets a wide variety of
       platforms.

   * - `scikit-image <https://github.com/scikit-image/scikit-image>`_
     - Another complex project using ``meson-python``.

   * - `siphash24 <https://github.com/dnicolodi/python-siphash24>`_
     - A very simple project. It demonstrates how Meson makes it trivial to
       compile a `CPython extension`_ written in `Cython`_ via a simple template
       engine and link it to a library compiled from a Meson sub-project. Also
       an example of how to use `cibuildwheel`_ to produce Python wheels for
       several platforms.


.. _CPython extension: https://docs.python.org/3/extending/extending.html
.. _CPython extensions: https://docs.python.org/3/extending/extending.html
.. _Cython: https://github.com/cython/cython
.. _Fortran: https://fortran-lang.org/
.. _Pythran: https://github.com/serge-sans-paille/pythran
.. _cibuildwheel: https://github.com/pypa/cibuildwheel
