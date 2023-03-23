.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-pyproject-settings:

***************************
``pyproject.toml`` settings
***************************

This page lists the configuration settings supported by
``meson-python`` in the ``pyproject.toml`` file.

.. option:: tool.meson-python.args.dist

   Extra arguments to be passed to the ``meson dist`` command.

.. option:: tool.meson-python.args.setup

   Extra arguments to be passed to the ``meson setup`` command.

.. option:: tool.meson-python.args.compile

   Extra arguments to be passed to the ``meson compile`` command.

.. option:: tool.meson-python.args.install

   Extra arguments to be passed to the ``meson install`` command.

Usage example:

.. code-block:: toml

   [tool.meson-python.args]
   setup = ['-Dwarning_level=2', '-Db_pie=true']
   dist = ['--include-subprojects']
   compile = ['-j4']
   install = ['--quiet']
