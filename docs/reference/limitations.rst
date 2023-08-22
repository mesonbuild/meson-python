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


Shared libraries on Windows
===========================

On Windows, ``meson-python`` cannot encapsulate shared libraries
installed as part of the Meson project into the Python wheel for
Python extension modules or executables, in a way suitable for them to
be found at run-time.

This limitation can be overcome with static linking or using
`delvewheel`_ to post-process the Python wheel to bundle the required
shared libraries and include the setup code to properly set the
library search path.


.. _install_data: https://mesonbuild.com/Reference-manual_functions.html#install_data
.. _importlib-resources: https://importlib-resources.readthedocs.io/en/latest/index.html
.. _delvewheel: https://github.com/adang1345/delvewheel

.. |install_data| replace:: ``install_data``
