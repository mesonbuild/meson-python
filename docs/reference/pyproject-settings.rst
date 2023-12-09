.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-pyproject-settings:

****************
Project settings
****************

This page lists the configuration settings supported by
``meson-python`` in the ``pyproject.toml`` file. Please refer to the
:ref:`how-to-guides-meson-args` guide for for information on how to
use them and examples.

.. option:: tool.meson-python.allow-windows-internal-shared-libs

   Enable support for relocating internal shared libraries that would be
   installed into the system shared library location to the
   ``.<package-name>.mesonpy.libs`` folder also on Windows. The relocation can
   be done transparently on UNIX platforms and on macOS, where the shared
   library load path can be adjusted via RPATH or equivalent mechanisms.
   Windows lacks a similar facility, thus the Python package is responsible to
   extend the DLL load path to include this directory or to preload the
   shared libraries. See :ref:`here <internal-shared-libraries>` for detailed
   documentation. This option ensures that the package authors are aware of
   this requirement.

.. option:: tool.meson-python.limited-api

   A boolean indicating whether the extension modules contained in the
   Python package target the `Python limited API`__.  Extension
   modules can be compiled for the Python limited API specifying the
   ``limited_api`` argument to the |extension_module()|__ function
   in the Meson Python module.  When this setting is set to true, the
   value ``abi3`` is used for the Python wheel filename ABI tag.

   This setting is automatically reverted to false when the
   ``-Dpython.allow_limited_api=false`` option is passed to ``meson
   setup``.

.. option:: tool.meson-python.meson

   A string specifying the ``meson`` executable or script to use. If it is a
   path to an existing file with a name ending in ``.py``, it will be invoked
   as a Python script using the same Python interpreter that is used to run
   ``meson-python`` itself. It can be overridden by the :envvar:`MESON`
   environment variable.

.. option:: tool.meson-python.args.dist

   Extra arguments to be passed to the ``meson dist`` command.

.. option:: tool.meson-python.args.setup

   Extra arguments to be passed to the ``meson setup`` command.

.. option:: tool.meson-python.args.compile

   Extra arguments to be passed to the ``ninja`` command.

.. option:: tool.meson-python.args.install

   Extra arguments to be passed to the ``meson install`` command.


__ https://docs.python.org/3/c-api/stable.html?highlight=limited%20api#stable-application-binary-interface
__ https://mesonbuild.com/Python-module.html#extension_module

.. |extension_module()| replace:: ``extension_module()``
