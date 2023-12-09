.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-limitations:

***********
Limitations
***********


Non-package data files
======================

It is possible to encapsulate arbitrary data files into Python
wheels. ``meson-python`` will add to the wheel any data file installed
into the Meson's ``{datadir}`` location, for example via Meson's
|install_data()|_ function. However, when the resulting wheel is
installed, these files are unpacked into a platform-specific location
and there is no supported facility to reliably find them at run time.

It is recommended to include data files than need to be accessible at
run-time inside the package alongside the Python code, and use
:mod:`importlib.resources` (or the `importlib-resources`_ backport) to
access them.


.. _install_data(): https://mesonbuild.com/Reference-manual_functions.html#install_data
.. _importlib-resources: https://importlib-resources.readthedocs.io/en/latest/index.html

.. |install_data()| replace:: ``install_data()``
