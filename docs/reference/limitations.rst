.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-limitations:

***********
Limitations
***********


No data
=======

Data, as installed by |install_data|_, is not supported.  It is
recommended to install data files alongside the Python modules that
requires them, and use :py:mod:`importlib.resources` (or the
:py:mod:`importlib_resources` backport) to access it.


Platform-specific limitations
=============================


Executables with internal dependencies :bdg-warning:`Windows`
-------------------------------------------------------------


If you have an executable that links against a shared library provided by your
project, on Windows ``meson-python`` will not be able to correctly bundle it
into the *wheel*.

The executable will be included in the *wheel*, but it
will not be able to find the project libraries it links against.

This is, however, easily solved by using a static library for the executable in
question.

.. _install_data: https://mesonbuild.com/Reference-manual_functions.html#install_data

.. |install_data| replace:: ``install_data``
