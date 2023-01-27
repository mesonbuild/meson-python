.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-pyproject-settings:

***************************
``pyproject.toml`` settings
***************************

This page lists the configuration settings supported by ``meson-python`` in the
``pyproject.toml`` file.


.. list-table::
   :widths: 35 65
   :header-rows: 1
   :stub-columns: 1

   * - Setting name
     - Description

   * - ``tool.meson-python.args.dist``
     - Extra arguments to be passed to the ``meson dist`` command

   * - ``tool.meson-python.args.setup``
     - Extra arguments to be passed to the ``meson setup`` command.

   * - ``tool.meson-python.args.compile``
     - Extra arguments to be passed to the ``meson compile`` command.

   * - ``tool.meson-python.args.install``
     - Extra arguments to be passed to the ``meson install`` command.
