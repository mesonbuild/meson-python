.. SPDX-FileCopyrightText: 2021 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. Contributors list for the latest release can be generated with

   git log --format='%aN' $PREV..HEAD | sort -u | awk '$1=$1' RS='' FS='\n' OFS=', '


+++++++++
Changelog
+++++++++

0.14.0
======

- Do not run ``meson install`` to build a wheel. This was unnecessary
  as files are added to the wheel from the build and source
  directories. This does not affect the handling of ``meson install``
  options, which are interpreted by ``meson-python`` itself.
- Obey the ``--skip-subprojects`` when specified for the ``meson
  install`` command.
- Implement support for the ``exclude_directories`` and
  ``exclude_files`` arguments to Meson ``install_subdir()`` function
  and similar installation functions. This requires Meson version
  1.1.0 or later.
- Implement support for building wheels targeting the Python limited
  API. Extension modules targeting the Python limited API can be
  easily built starting with the upcoming Meson 1.3.0 release.
- when ``pyproject.toml`` does not contain a ``version`` field and
  ``version`` is not declared dynamic, raise an error instead of
  silently using the version declared in ``meson.build``.
- Fix the mtime of source files in the sdist tarball.
- Add ``objc`` and ``objcpp`` compilers to the cross file generated
  when the ``$ARCHFLAGS`` is set.
- Extensive documentation improvements.

Charles Brunet, Daniele Nicolodi, Henry Schreiner, Michał Górny, Ralf
Gommers --- xx-09-2023


0.13.2
======

- Fix system name in cross file generated when using ``$ARCHFLAGS``.
- Fix handling of ``null`` Meson install tags.

Charles Brunet, Daniele Nicolodi --- 22-06-2023.


0.13.1
======

- Fix regression in cross-compilation via ``$ARCHFLAGS`` on macOS where the
  cross file was written in the build directory before it was created,
  resulting in an error.
- Do not require setting ``$_PYTHON_HOST_PLATFORM`` when cross-compiling via
  ``$ARCHFLAGS`` on macOS.
- Add the ``--quiet`` option when invoking ``meson install``. The installation
  paths are a detail of the ``meson-python`` implementation and are generally
  not interesting for the user.
- Fix terminal logging when overriding the current line when listing files
  added to the wheel.
- Improve the error message emitted when a package split between the
  ``purelib`` and ``platlib`` wheel locations is detected.

Daniele Nicolodi, Ralf Gommers --- 28-04-2023.


0.13.0
======

- Add support for editable installs.
- Adjust the default build options passed to ``meson setup``.
- Make sure that the directory where the wheel or sdist build artifacts are
  created exists. Fixes building with PDM.
- Fix the specification of the C++ compiler for cross-compilation with
  ``$ARCHFLAGS`` on macOS.
- Pass the ``--reconfigure`` option to ``meson setup`` if and only if the
  specified build directory exists and is a valid Meson build directory.
- Pass the ``--no-rebuild`` option to ``meson install``.
- Allow to select the files to be included in the wheel via Meson install tags
  passing the ``--tags`` option to ``meson install`` via ``pyproject.toml`` or
  config settings.
- Do not use the ``meson compile`` indirection to build the project, except on
  Windows, where it is required to setup the Visual Studio environment.
- Do not add ``ninja`` to the build dependencies if ``$NINJA`` is set but it
  does not point to a ``ninja`` executable with the required minimum version.
- Verify at run time that Meson satisfies the minimum required version.
- Place native and cross files in the build directory instead of in the
  source directory.
- Drop the ``typing-extensions`` package dependency.
- Add dependency on ``setuptools`` on Python 3.12 and later. This fixes build
  error due to Meson depending on the ``distutils`` standard library module
  removed in Python 3.12.
- Bump the required ``pyproject-metadata`` version to 0.7.1.
- Allows some more cross-compilation setups by not checking extension modules
  filename suffixes against the suffixes accepted by the current interpreter.
- Raise an error when a file that would be installed by Meson cannot be mapped
  to a wheel location.
- Raise an error when a package is split between ``platlib`` and ``purelib``.
- Do not generate a warning when ``pyproject.toml`` does not contain a
  ``project`` section and Python package metadata is derived from ``meson.build``.
- Improve reporting of ``pyproject.toml`` validation errors.
- Fix validation of tool specific options in ``pyproject.toml``. In
  particular, allows to specify an incomplete set of options in the
  ``tool.meson-python.args`` table.

Daniele Nicolodi, Doron Behar, Eli Schwartz, Filipe Laíns, Lars Pastewka,
Luigi Giugliano, Matthias Köppe, Peter Urban, Ralf Gommers, Stefan van der
Walt, Thomas Li --- 18-04-2023.


0.12.1
======

- Fix regression where the ``$MACOSX_DEPLOYMENT_TARGET`` environment variable
  was accidentally renamed to ``$MACOS_DEPLOYMENT_TARGET``.

Filipe Laíns, Stefan van der Walt --- 17-02-2023.


0.12.0
======

- Require the ``typing_extensions`` package for Python < 3.10 rather than for
  Python < 3.8 only.
- Emit an error message and raise ``SystemExit`` on expected errors.
- Revise error messages for consistency.
- Support setuptools-style macOS cross compilation via ``$ARCHFLAGS``.
- Allow to overwrite macOS platform tag via ``$_PYTHON_HOST_PLATFORM``.
- Include an hint with the most similar known option names in the error
  message emitted when an unknown config setting is encountered.

Daniele Nicolodi, Filipe Laíns, Henry Schreiner, Matthias Köppe, Thomas A
Caswell --- 22-12-2022.


0.11.0
======

- Project moved to the ``mesonbuild`` organization.
- Determine wheel tags by introspecting the Python interpreter.
- Allow users to pass options directly to Meson via the ``dist``, ``setup``,
  ``compile``, and ``install`` entries in the ``tools.meson-python.args``
  table in ``pyproject.toml``, or via the ``dist-args``, ``setup-args``,
  ``compile-args``, and ``install-args`` config settings.
- Use the system ``ninja`` if possible. Return ``ninja`` as a build dependency
  otherwise.
- Include files generated by ``mesonadd_dist_script`` in the sdist.
- Use ``tomllib`` on Python 3.11 or later.
- Drop the ``wheel`` package dependency.
- Fix bug where the ``entry_points.txt`` file was not generated.
- Fix bug where Cygwin Python extensions were not being noticed.

Ben Greiner, Daniele Nicolodi, Filipe Laíns, Henry Schreiner, Matthias Köppe,
Ralf Gommers, Sam Thursfield, Thomas Li --- 21-11-2022.


0.10.0
======

- Ignore the minor version on macOS 11 or later, to match the behavior of
  ``pypa/packaging``.

Filipe Laíns, Ralf Gommers --- 05-10-2022.


0.9.0
=====

- More fixes on ABI tag detection.
- Fix incorrect tag on 32-bit Python running on a x86_64 host.
- Fix sdist permissions.
- Fix incorrect PyPy tags.
- Fix ``install_subdirs`` not being included in wheels.
- Take ``MACOSX_DEPLOYMENT_TARGET`` into account for the platform tag.
- Don't set the rpath on binaries if unneeded.

Eli Schwartz, Filipe Laíns, Matthias Köppe, Peyton Murray, Ralf Gommers,
Thomas Kluyver, Thomas Li --- 29-09-2022.


0.8.1
=====

- Fix ``UnboundLocalError`` in tag detection code.

Filipe Laíns, Ralf Gommers --- 28-07-2022.


0.8.0
=====

- Fix sometimes the incorrect ABI tags being generated.
- Add workaround for macOS 11 and 12 installations that are missing a minor
  version in the platform string.

Filipe Laíns --- 26-07-2022.


0.7.0
=====

- Fix the wrong Python and ABI tags being generated in Meson 0.63.0.
- Fix project license not being included in the project metadata.

Filipe Laíns, Ralf Gommers --- 22-07-2022.


0.6.0
=====

- Project re-licensed to MIT.
- Error out when running in an unsupported interpreter.
- Fix slightly broken Debian heuristics.
- Update ``pep621`` dependency to ``pyproject-metadata``.

Filipe Laíns, Ralf Gommers, Thomas A Caswell --- 21-06-2022.


0.5.0
=====

- Improvements in dependency detections.
- Include uncommited changes in sdists.

Filipe Laíns --- 26-05-2022.


0.4.0
=====

- Set sane default arguments for release builds.

Filipe Laíns --- 06-05-2022.


0.3.0
=====

- Initial cross-platform support.
- Bundling libraries is still only supported on Linux.
- Add initial documentation.
- The build directory is now located in the project source.

Filipe Laíns, Rafael Silva --- 23-03-2022.


0.2.1
=====

- Fix getting the project version dynamically from Meson.

Filipe Laíns --- 26-02-2022.


0.2.0
=====

- Select the correct ABI and Python tags.
- Force Meson to use the correct Python executable.
- Replace auditwheel with in-house vendoring mechanism.

Filipe Laíns --- 24-01-2022.


0.1.2
=====

- Fix auditwheel not being run.

Filipe Laíns --- 12-11-2021.


0.1.1
=====

- Fix minor compatibility issue with Python < 3.9.

Filipe Laíns --- 28-10-2021.


0.1.0
=====

- Initial release.

Filipe Laíns --- 28-10-2021.
