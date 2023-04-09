.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _explanations-default-options:

*********************
Default build options
*********************

Meson offers many `built-in options`__ to control how the project is
built and installed. In the vast majority of cases those have good
defaults. There are however a few options that ``meson-python``
overrides with its own defaults to adjust the build process to the
task of building Python wheels.

The default options specified by ``meson-python`` are overridden by
package specific options specified in ``pyproject.toml`` and by
options provided by the user at build time via the Python build
front-end. Refer to the :ref:`how-to-guides-meson-args` guide for
details.

The options used to build the project are summarized in the *User
defined options* section of the output of the ``meson setup`` stage of
the build, for example when running ``python -m build -w``. This will
look something like:

__ https://mesonbuild.com/Builtin-options.html

.. code-block:: text

    User defined options
      Native files: $builddir/meson-python-native-file.ini
      buildtype   : release
      b_ndebug    : if-release
      b_vscrt     : md

where the path to the build directory has been replaced with
``$builddir`` for clarity.

The options that ``meson-python`` specifies by default are:

.. option:: native-file=$builddir/meson-python-native-file.ini

   ``meson-python`` uses a native file to point Meson at the
   ``python`` interpreter that the build must target. This is the
   Python interpreter that is used to run the Python build
   front-end. Meson would otherwise look for the first Python
   interpreter on the ``$PATH``, which may not be the same.

   Additional ``--native-file`` options can be passed to ``meson
   setup`` if further adjustments to the native environment need to be
   made. Meson will merge the contents of all machine files. To ensure
   everything works as expected, the ``meson-python`` native file is
   last in the command line, overriding the ``python`` binary path
   that may have been specified in user supplied native files.

.. option:: buildtype=release

   The Meson default is to produce a debug build with binaries
   compiled with debug symbols and, when compiling with MSVC, linking
   to the Visual Studio debug runtime, see below. The main purpose of
   ``meson-python`` is to build release artifacts, therefore a more
   appropriate `build type`__ is selected. A release build is compiled
   without debug symbols and with compiler optimizations. Refer to the
   `Meson documentation`__ for more details.

__ https://mesonbuild.com/Builtin-options.html#details-for-buildtype
__ https://mesonbuild.com/Builtin-options.html#core-options

.. option:: b_ndebug=if-release

   For reasons related to backward compatibility, Meson does not
   disable assertions for release builds. For most users this is a
   surprising and undesired behavior. This option instructs Meson to
   pass the ``-DNDEBUG`` option to the compilers, unless the build
   type is set to something else than release.

.. option:: b_vscrt=md

   With the default options, when compiling a debug build, Meson
   instructs the MSVC compiler to use the debug version of the Visual
   Studio runtime library. This causes the MSVC linker to look for the
   debug build of all the linked DLLs. The Python distribution for
   Windows does not contain a debug version of the Python DLL and
   linking fails. These linking failures are surprising and hard to
   diagnose. To avoid this issue when users explicitly asks for a
   debug build, ``meson-python`` sets this options to instruct Meson
   to compile with the release version of the Visual Studio
   runtime. For more details, refer to the `Meson documentation`__ and
   to the `Visual Studio documentation`__ . This option is ignored
   when other compilers are used.

__ https://mesonbuild.com/Builtin-options.html#base-options
__ https://learn.microsoft.com/en-us/cpp/build/reference/md-mt-ld-use-run-time-library?view=msvc-170
