.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-environment-variables:

*********************
Environment variables
*********************


.. todo::

   - Document ``ARCHFLAGS`` (see `#226`_)


.. list-table::
   :widths: 35 65
   :header-rows: 1
   :stub-columns: 1

   * - Name
     - Description

   * - ``NO_COLOR``
     - Disables color output from messages by ``meson-python``.See
       https://no-color.org for more information.

       .. admonition:: Conflicts with other options
          :class: attention

          Cannot be used at the same time as ``FORCE_COLOR``.

   * - ``FORCE_COLOR``
     - Forces color output from messages by ``meson-python``.

       .. admonition:: Conflicts with other options
          :class: attention

          Cannot be used at the same time as ``NO_COLOR``.

   * - ``MESONPY_EDITABLE_VERBOSE``
     - Enables verbose output in editable installs.

       .. admonition:: Check our guide
          :class: seealso

          Please check our :ref:`how-to-guides-editable-installs` guide for more
          information on how to use it.

   * - ``MACOSX_DEPLOYMENT_TARGET``
     - Specify the target macOS version.

       If ``MACOSX_DEPLOYMENT_TARGET`` is set, we will use the selected version
       for the *wheel* tag.

       .. admonition:: Use the right version
          :class: attention

          Please use major versions only, so ``10.13``, ``11``, ``12``.

       If ``MACOSX_DEPLOYMENT_TARGET`` is not set, the current macOS major
       version on the build machine will be used instead (derived from
       :py:meth:`platform.mac_ver`).

       .. admonition:: macOS versioning
          :class: note

          macOS versioning changed from macOS 11 onward. For macOS 10.x, the
          versioning scheme is ``10.major.minor``. From macOS 11, it is
          ``major.minor.bugfix``. Wheel tags and deployment targets are currently
          designed to be for major versions only. Examples of the platform part
          of tags that are currently accepted by, e.g., ``pip`` are:
          ``macosx_10_9``, ``macosx_10_13``, ``macosx_11_0``, ``macosx_12_0``.

       .. admonition:: Specifying the target version via the compiler
          :class: note

          Another way of specifying the target macOS platform is to explicitly
          use ``-mmacosx-version-min`` compile and link flags when invoking
          Clang_ or GCC_. It is not possible for ``meson-python`` to detect this
          though, so it will not set the *wheel* tag to that flag automatically.

   * - ``NINJA``
     - Specify the ninja_ executable to use. Can also be used to select ninja_
       alternatives like samurai_.


.. _#226: https://github.com/mesonbuild/meson-python/pull/226
.. _Clang: https://clang.llvm.org
.. _GCC: https://gcc.gnu.org
.. _ninja: https://ninja-build.org
.. _samurai: https://github.com/michaelforney/samurai
