.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-pyproject-settings:

***************************
``pyproject.toml`` settings
***************************

This page lists the configuration settings supported by
``meson-python`` in the ``pyproject.toml`` file. Please refer to the
:ref:`how-to-guides-meson-args` guide for for information on how to
use them and examples.

.. option:: tool.meson-python.args.dist

   Extra arguments to be passed to the ``meson dist`` command.

.. option:: tool.meson-python.args.setup

   Extra arguments to be passed to the ``meson setup`` command.

.. option:: tool.meson-python.args.compile

   Extra arguments to be passed to the ``ninja`` command.

.. option:: tool.meson-python.args.install

   Extra arguments to be passed to the ``meson install`` command.
