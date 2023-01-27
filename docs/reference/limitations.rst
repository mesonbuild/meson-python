.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-limitations:

***********
Limitations
***********


No data
=======

Data, as installed by |install_data|_, is not supported.

We recommend you install your data inside a Python module and use
:py:mod:`importlib.resources` (or the :py:mod:`importlib_resources` backport) to
access it. You can check our :ref:`tutorials-data` tutorial for how to do this.

If you really need the data to be installed where it was previously (eg.
``/usr/data``), you can do so at runtime.


Parallel use of editable installs
=================================

Currently, using a package installed in editable mode in more than one
interpreter instances at the same time is not supported.


Using editable installs with IDEs
=================================

Currently, with editable installs, setting breakpoints via an IDE or similar
tool will not work.

We have work planned to fix this issue.


Platform-specific limitations
=============================


Executables with internal dependencies :bdg-warning:`Windows` :bdg-warning:`macOS`
----------------------------------------------------------------------------------


If you have an executable that links against a shared library provided by your
project, on Windows and macOS ``meson-python`` will not be able to correctly
bundle it into the *wheel*.

The executable will be included in the *wheel*, but it
will not be able to find the project libraries it links against.

This is, however, easily solved by using a static library for the executable in
question. Find how to do this in our
:ref:`how-to-guides-executable-with-internal-dependencies` guide.


.. _install_data: https://mesonbuild.com/Reference-manual_functions.html#install_data

.. |install_data| replace:: ``install_data``
