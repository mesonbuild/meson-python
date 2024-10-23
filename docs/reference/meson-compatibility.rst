.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _meson-compatibility:

*******************
Meson compatibility
*******************

``meson-python`` tightly integrates with Meson to produce Python
wheels and sdists. Therefore, correct operation depends on
functionality implemented by Meson.  ``meson-python`` strives to
maintain compatibility with as old as possible Meson releases.
However, some functionality is available only with more recent Meson
versions.

.. option:: 0.63.3

   Meson is 0.63.3 is the minimum required version.

.. option:: 1.1.0

   Meson 1.1.0 or later is required to support the ``exclude_files``
   and ``exclude_directories`` arguments to Meson ``install_subdir()``
   and similar installation functions. On older Meson versions, these
   arguments have no effect.

.. option:: 1.2.3

   Meson 1.2.3 or later is required to support Python 3.12 or later.
   Since version 1.2.3, Meson does not rely anymore on the
   ``distutils`` module, which was removed from the standard library
   in Python 3.12. When installed on Python 3.12, ``meson-python``
   depends on Meson 1.2.3 or later.

.. option:: 1.3.0

   Meson 1.3.0 or later is required for compiling extension modules
   targeting the Python limited API.

.. option:: 1.6.0

   Meson 1.6.0 or later is required to support ``license`` and
   ``license-files`` dynamic fields in ``pyproject.toml`` and to
   populate the package license and license files from the ones
   declared via the ``project()`` call in ``meson.build``. This also
   requires ``pyproject-metadata`` version 0.9.0 or later.

Build front-ends by default build packages in an isolated Python
environment where build dependencies are installed. Most often, unless
a package or its build dependencies declare explicitly a version
constraint, this results in the most recent version of the build
dependencies to be installed. However, if a package uses
functionalities implemented only in combination with a specific Meson
version, it is recommended to explicitly declare a version
requirement in ``pyproject.toml``. For example:

.. code-block:: toml

   [build-system]
   build-backend = 'mesonpy'
   requires = [
     'meson-python',
     'meson >= 1.1.0',
   ]
