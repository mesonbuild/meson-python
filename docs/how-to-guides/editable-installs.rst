.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-editable-installs:

*****************
Editable installs
*****************

We have support for editable installs! To use it, simply pass the
``-e``/``--editable`` option to pip_.


.. code-block:: console

   $ pip install -e .


This will install the project in the current directory in editable mode. When a
``meson-python`` package is installed in editable mode, it will be re-built the
first time it is imported. That means, the first time you import a module from
your package, it will take a bit longer.


.. admonition:: What is the scope of editable installs?
   :class: seealso

   The editable installs feature only targets the Python modules of the project.

   This does include, though, native modules, which can be written in C, C++,
   Rust_, Cython_, etc. With ``meson-python`` such modules will be
   automatically rebuilt when using editable installs.

   Metadata-based features, like `entry points`_, and similar mechanisms will
   not be updated when using editable installs. This is a limitation of editable
   installs specification itself.


.. _how-to-guides-editable-installs-verbose:

Verbose mode
============

It might be useful for you to see the output of Meson_ when the package is being
re-built. We provide a *verbose mode* that does this, and can be enabled either
temporarily, after the install, or permanently, in the install.


To enable the verbose mode on any existing ``meson-python`` editable install,
you simply need to set the ``MESONPY_EDITABLE_VERBOSE`` environment variable
to any non-null value.


.. code-block:: console

   $ MESONPY_EDITABLE_VERBOSE=1 python


To enable verbose mode permanently, you simply need to set the
``editable-verbose`` :ref:`config setting <reference-config-settings>` to any
non-null value when installing the package.

With pip_, you can do this as follows:


.. code-block:: console

   $ python -m pip install -e . --config-settings editable-verbose=true


.. admonition:: ``MESONPY_EDITABLE_VERBOSE`` will have no effect here
   :class: attention

   Please note that the ``MESONPY_EDITABLE_VERBOSE`` environment variable will
   not have **any** effect on the installation, it simply forces verbose mode to
   be enabled **after** the package has been installed.


.. _pip: https://github.com/pypa/pip
.. _Rust: https://www.rust-lang.org/
.. _Cython: https://github.com/cython/cython
.. _entry points: https://packaging.python.org/en/latest/specifications/entry-points/
.. _Meson: https://github.com/mesonbuild/meson
