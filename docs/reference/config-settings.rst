.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-config-settings:

*********************
Build config settings
*********************

This page lists the build configuration settings, that is, the settings you can
pass when building the project. Please check our
:ref:`how-to-guides-meson-args` guide for information on how to use them.


.. list-table::
   :widths: 20 80
   :header-rows: 1
   :stub-columns: 1

   * - Setting name
     - Description

   * - ``builddir``
     - Selects the Meson_ build directory to use. If the directory already
       exists, it will be re-used, if it does not exists, it will be created.
       This lets you avoid rebuilding the whole project from scratch when
       developing. It is also useful if you want to configure the build
       yourself.

       .. admonition:: Use at your own risk
          :class: warning

          Re-using a build directory that was not configured by ``meson-python``
          can cause issues, so use at your own risk. We cannot fully support
          this use-case, but will try to fix issues where possible and
          reasonably viable.

          Passing this option with a non-existent build directory, letting
          ``meson-python`` configure it, and then passing it again on subsequent
          builds, is perfectly fine. Just be sure to delete the build directory
          after changing the ``meson-python`` version, as that might cause
          issues.

   * - ``dist-args``
     - Extra arguments to be passed to the ``meson dist`` command. The arguments
       are placed after the :ref:`reference-pyproject-settings` ones.

   * - ``setup-args``
     - Extra arguments to be passed to the ``meson setup`` command. The
       arguments are placed after the :ref:`reference-pyproject-settings` ones.

   * - ``compile-args``
     - Extra arguments to be passed to the ``meson compile`` command. The
       arguments are placed after the :ref:`reference-pyproject-settings` ones.

   * - ``install-args``
     - Extra arguments to be passed to the ``meson install`` command. The
       arguments are placed after the :ref:`reference-pyproject-settings` ones.

   * - ``editable-verbose``
     - Enable :ref:`verbose mode <how-to-guides-editable-installs-verbose>` on
       editable an install.

       .. admonition:: Only valid on editable installs
          :class: attention

          This option is only valid when building the project for an editable
          install. Please check our :ref:`how-to-guides-editable-installs` guide
          for more information.


.. admonition:: Check our guides
   :class: seealso

   Check our guides to learn more about how to use these settings:

   - :ref:`how-to-guides-build-directory`
   - :ref:`how-to-guides-meson-args`
   - :ref:`how-to-guides-editable-installs`


.. _Meson: https://github.com/mesonbuild/meson
