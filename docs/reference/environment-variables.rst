.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-environment-variables:

*********************
Environment variables
*********************

Environment variables can be used to influence ``meson-python``'s behavior, as
well as the behavior of Meson and other tools that may be used during the
build. This page lists all the environment variables directly used by
``meson-python``.

Meson recommends using command line arguments instead of environment variables,
but does support a number of environment variables for compatibility with other
build systems:

- `Compiler and linker flag variables <https://mesonbuild.com/Reference-tables.html#compiler-and-linker-flag-environment-variables>`__
- `Compiler and linker selection variables <https://mesonbuild.com/Reference-tables.html#compiler-and-linker-selection-variables>`__

Other environment variables may influence how other tools used during the setup
or build steps operate. For example, ``pkg-config`` supports
``PKG_CONFIG_PATH`` which influences the search path for ``.pc`` files
describing the available dependencies.

.. warning::

    Conda sets a number of environment variables during environment activation
    for compiler/linker selection (``CC``, ``CXX``, ``FC``, ``LD``) and
    compile/link flags (``CFLAGS``, ``CXXFLAGS``, ``FFLAGS``, ``LDFLAGS``) when
    compilers are installed in a conda environment. This may have unexpected
    side effects (see for example the note in
    :ref:`how-to-guides-debug-builds`).


Environment variables used by meson-python
==========================================

.. envvar:: ARCHFLAGS

   This environmental variable is used for supporting architecture cross
   compilation on macOS in a way compatible with setuptools_. It is ignored on
   all other platforms. It can be set to ``-arch arm64`` or to ``-arch
   x86_64`` for compiling for the arm64 and the x86_64 architectures
   respectively. Setting this environment variable to any other value is not
   supported.

   The macOS toolchain allows architecture cross compilation passing the
   ``-arch`` flat to the compilers. ``meson-python`` inspects the content of
   this environment variable and synthesizes a Meson `cross build definition
   file`_ with the appropriate content, and passes it to ``meson setup`` via
   the ``--cross-file`` option.

   Support for this environment variable is maintained only for
   compatibility with existing tools, cibuildwheel_ in particular, and
   is not the recommended solution for cross compilation.

.. _setuptools: https://setuptools.pypa.io/en/latest/setuptools.html
.. _cross build definition file: https://mesonbuild.com/Cross-compilation.html
.. _cibuildwheel: https://cibuildwheel.readthedocs.io/en/stable/

.. envvar:: IPHONEOS_DEPLOYMENT_TARGET

   This environment variable is used to specify the target iOS platform version
   to the Xcode development tools.  If this environment variable is set,
   ``meson-python`` will use the specified iOS version for the Python wheel
   platform tag, instead than the iOS platform default of 13.0.

   This variable must be set to a major/minor version, for example ``13.0`` or
   ``15.4``.

   Note that ``IPHONEOS_DEPLOYMENT_TARGET`` is the only supported mechanism
   for specifying the target iOS version. Although the iOS toolchain supports
   the use of ``-mios-version-min`` compile and link flags to set the target iOS
   version, ``meson-python`` will not set the Python wheel platform tag
   correctly unless ``IPHONEOS_DEPLOYMENT_TARGET`` is set.

.. envvar:: FORCE_COLOR

   Setting this environment variable to any value forces the use of ANSI
   escape sequences to colorize the ``meson-python``'s console output. Setting
   both ``NO_COLOR`` and ``FORCE_COLOR`` environment variables is an error.

.. envvar:: MACOSX_DEPLOYMENT_TARGET

   This environment variable is used to specify the target macOS platform major
   version to the Xcode development tools.  If this environment variable is set,
   ``meson-python`` will use the specified macOS version for the Python wheel
   platform tag instead than the macOS version of the build machine.

   This variable must be set to macOS major versions only: ``10.9`` to
   ``10.15``, ``11``, ``12``, ``13``, ...

   Please note that the macOS versioning changed from macOS 11 onward. For
   macOS 10, the versioning scheme is ``10.$major.$minor``. From macOS 11
   onward, it is ``$major.$minor.$bugfix``. Wheel tags and deployment targets
   are currently designed to specify compatibility only with major version
   number granularity.

   Note that ``MACOSX_DEPLOYMENT_TARGET`` is the only supported mechanism for
   specifying the target macOS version. Although the macOS toolchain supports
   the use of ``-mmacosx-version-min`` compile and link flags to set the target
   macOS version, ``meson-python`` will not set the Python wheel platform tag
   correctly unless ``MACOSX_DEPLOYMENT_TARGET`` is set.

.. envvar:: MESON

   Specifies the ``meson`` executable or script to use. It overrides
   ``tool.meson-python.meson``. See :ref:`reference-pyproject-settings` for
   more details.

.. envvar:: MESONPY_EDITABLE_VERBOSE

   Setting this environment variable to any value enables directing to the
   console the messages emitted during project rebuild triggered by imports of
   editable wheels generated by ``meson-python``. Refer to the
   :ref:`how-to-guides-editable-installs` guide for more information.

.. envvar:: NINJA

   Specifies the ninja_ executable to use. It can also be used to select
   ninja_ alternatives like samurai_.

.. _ninja: https://ninja-build.org
.. _samurai: https://github.com/michaelforney/samurai

.. envvar:: NO_COLOR

   Setting this environment variable to any value disables the use of ANSI
   terminal escape sequences to colorize ``meson-python``'s console
   output. Setting both ``NO_COLOR`` and ``FORCE_COLOR`` environment variables
   is an error.
