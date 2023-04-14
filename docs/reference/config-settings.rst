.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-config-settings:

*********************
Build config settings
*********************

This page lists the build configuration settings, that is, the
settings you can pass when building the project. Please refer to the
:ref:`how-to-guides-config-settings` and
:ref:`how-to-guides-meson-args` guides for information on how to use
them.

.. option:: builddir

   By default ``meson-python`` uses a temporary builds directory.
   This settings allows to select the Meson build directory and
   prevents it to be deleted when ``meson-python`` terminates.  If the
   directory does not exists, it will be created.  If the directory
   exists and contains a valid Meson build directory setup, the
   project will be reconfigured using ``meson setup --reconfigure``.

   The same build directory can be used by subsequent invocations of
   ``meson-python``. This avoids having to rebuild the whole project
   when testing changes during development.

.. option:: dist-args

   Extra arguments to be passed to the ``meson dist`` command.

.. option:: setup-args

   Extra arguments to be passed to the ``meson setup`` command.

.. option:: compile-args

   Extra arguments to be passed to the ``ninja`` command.

.. option:: install-args

   Extra arguments to be passed to the ``meson install`` command.

.. option:: editable-verbose

   Enable :ref:`verbose mode <how-to-guides-editable-installs-verbose>`
   when building for an :ref:`editable install <how-to-guides-editable-installs>`.
