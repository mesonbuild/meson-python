.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-editable-installs:

*****************
Editable installs
*****************

Editable installs are a Python package installation mode designed to
facilitate package development. When a package is installed in
editable mode, edits to the project source code become effective
without the need of a new installation step. Editable installs are a
build backend independent formalization__ of the *development mode*
introduced by setuptools__.

__ https://peps.python.org/pep-0660/
__ https://setuptools.pypa.io/en/latest/userguide/development_mode.html

While most Python build backends apply development mode or editable
installs to the pure Python components, ``meson-python`` extends
editable installs to package components that require a compilation
step such as extension modules.

To install a package in editable mode, pass the ``--editable`` or
``-e`` option to ``pip install``. The editable installation mode
implies that the source code of the project being installed is
available in a local directory. To install the project in the current
directory in editable mode install the project's build dependencies in
your development environment and run

.. code-block:: console

   $ python -m pip install --no-build-isolation --editable .

This will install a stub in the Python site packages directory that
loads the package content from the sources and build directory. The
same stub is responsible to rebuild the compiled parts of the package
when the package is imported the first time in a given Python
interpreter instance. Because of the very fast partial rebuilds
allowed by Meson and ``ninja``, the rebuild has an almost negligible
impact on the import times.

Please note that some kind of changes, such as the addition or
modification of `entry points`__, or the addition of new dependencies, and
generally all changes involving package metadata, require a new
installation step to become effective.

__ https://packaging.python.org/en/latest/specifications/entry-points/

An editable install exposes at least all the files that would be
available in a regular installation. However, depending on the file
and directory organization in your project, it might also expose files
that would not be normally available.


Build dependencies
------------------

Because packages installed in editable mode are rebuilt on import, all
build dependencies need to available at execution time in the
development environment.

By default, pip builds packages in a isolated environment where build
dependencies are installed without affecting the user environment.
Packages installed in editable mode using build isolation will fail to
rebuild when imported, unless build dependencies are also installed in
the development environment. Furthermore, when build using build
isolation, a package that depends on headers or other resources
provided by its build dependencies, would resolve the path to these in
the isolated build environment. The isolated build environment is
deleted after the build is completed, resulting in failures when the
package in rebuild on import. For these reasons, when installing
packages in editable mode, it is recommended to disable build
isolation passing the ``--no-build-isolation`` argument to pip.

At the time of writing, pip does not offer a command to install a the
build dependencies for a package. The build dependencies requirements
can be obtained inspecting ``pyproject.toml`` for the package to be
installed. These include at least the ``meson-python`` Python package,
and the ``meson`` and ``ninja`` Python packages, if the respective
commands are not provided by the system, or if they are not the
required version:

.. code-block:: console

   $ python -m pip install meson-python meson ninja


Build directory
---------------

Because the compiled components of the package are loaded directly
from the build directory, the build directory needs to be available
alongside the source directory at execution time.

When building a package in editable mode, ``meson-python`` uses a
build directory named as the wheel ABI tag associated to the
interpreter for which the package is being build. The build directory
is placed in a directory named ``build`` inside the source tree. For
example, an editable installation for CPython 3.11 will be associated
to a ``build/cp311/`` build directory. This directory structure allows
to install the same project in editable mode for multiple interpreters
with different ABIs.

An alternative build directory can be specified using the
:option:`builddir` config setting.


.. _how-to-guides-editable-installs-verbose:

Verbose mode
------------

Because editable installation are mostly a package development aid, it
might be often useful to be able to inspect the compilation log.
Setting the :envvar:`MESONPY_EDITABLE_VERBOSE` environment variable
will result in the output of the build process to be emitted when a
package is rebuilt on import.  To enable this verbose mode permanently
for a package, the :option:`editable-verbose` config setting can be
set to a non-null value when installing the package:

.. code-block:: console

   $ python -m pip install --no-build-isolation --config-settings=editable-verbose=true --editable .
