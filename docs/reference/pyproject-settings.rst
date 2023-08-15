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
