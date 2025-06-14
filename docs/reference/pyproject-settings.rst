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
   Python package target the `Python limited API`_.  Extension
   modules can be compiled for the Python limited API specifying the
   ``limited_api`` argument to the |extension_module()|_ function
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

.. option:: tool.meson-python.wheel.exclude

   List of glob patterns matching paths of files that must be excluded from
   the Python wheel. The accepted glob patterns are the ones implemented by
   the Python :mod:`fnmatch` with case sensitive matching. The paths to be
   matched are as they appear in the Meson introspection data, namely they are
   rooted in one of the Meson install locations: ``{bindir}``, ``{datadir}``,
   ``{includedir}``, ``{libdir_shared}``, ``{libdir_static}``, et cetera.

   Inspecting the `Meson introspection data`_ may be useful to craft the exclude
   patterns. It is accessible as the ``meson-info/intro-install_plan.json`` JSON
   document in the build directory.

   This configuration setting is measure of last resort to exclude installed
   files from a Python wheel. It is to be used when the project includes
   subprojects that do not allow fine control on the installed files. Better
   solutions include the use of Meson install tags and excluding subprojects
   to be installed via :option:`tool.meson-python.args.install`.

.. option:: tool.meson-python.wheel.include

   List of glob patterns matching paths of files that must not be excluded
   from the Python wheel. All files recorded for installation in the Meson
   project are included in the Python wheel unless matching an exclude glob
   pattern specified in :option:`tool.meson-python.wheel.exclude`. An include
   glob pattern is useful exclusively to limit the effect of an exclude
   pattern that matches too many files.

.. _python limited api: https://docs.python.org/3/c-api/stable.html?highlight=limited%20api#stable-application-binary-interface
.. _extension_module(): `https://mesonbuild.com/Python-module.html#extension_module
.. _meson introspection data: https://mesonbuild.com/IDE-integration.html#install-plan

.. |extension_module()| replace:: ``extension_module()``
