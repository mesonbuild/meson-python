.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

:orphan:

.. _explanations-design-old:

*******************************
How does ``meson-python`` work?
*******************************


.. admonition:: Old documentation
   :class: attention

   You are looking at the old documentation. We are currently in the process of
   refactoring the whole documentation and this page was part of the old
   version. While it still contains lots of relevant information, it is not
   necessarily in the format we ultimately want to present, and is not well
   integrated with the other parts of the documentation.



How does it work?
=================

We implement the Python build system hooks, enabling any standards compliant
Python tool (pip_, `pypa/build`_, etc.) to build and install the project.

``meson-python`` will build a Python sdist (source distribution) or
wheel (binary distribution) from Meson_ project.

Source distribution (sdist)
---------------------------

The source distribution is based on ``meson dist``, so make sure all your files
are included there. In git projects, Meson_ will not include files that are not
checked into git, keep that in mind when developing. By default, all files
under version control will be included in the sdist. In order to exclude files,
use ``export-ignore`` or ``export-subst`` attributes in ``.gitattributes`` (see
the ``git-archive`` documentation for details; ``meson dist`` uses
``git-archive`` under the hood).

Local (uncommitted) changes to files that are under version control will be
included. This is often needed when applying patches, e.g. for build issues
found during packaging, to work around test failures, to amend the license for
vendored components in wheels, etc.

Binary distribution (wheels)
----------------------------

The binary distribution is built by running Meson_ and introspecting the build
and trying to map the files to their correct location. Due to some limitations
and/or bugs in Meson_, we might not be able to map some of the files with
certainty. In these cases, we will take the safest approach and warn the user.
In some cases, we might need to resort to heuristics to perform the mapping,
similarly, the user will be warned. These warnings are not necessarily a reason
for concern, they are there to help identifying issues. In these cases, we
recommend that you check if the files in question were indeed mapped to the
expected place, and open a bug report if they weren't.

If the project itself includes shared libraries that are needed by other files,
those libraries will be included in the wheel, and native files will have their
library search path extended to include the directory where the libraries are
placed.

If the project depends on external shared libraries, those libraries will not
be included in the wheel. This can be handled in several ways by the package
developer using ``meson-python``:

1. Finding or creating a suitable Python package that provides those shared
   libraries and can be added to ``dependencies`` in ``pyproject.toml``.
2. Vendoring those libraries into the wheel. Currently ``meson-python`` does
   not provide an OS-agnostic way of doing that; on Linux ``auditwheel`` can be
   used, and on macOS ``delocate``. Or, the package developer can copy the
   shared libraries into the source tree and patch ``meson.build`` files to
   include them.
3. Documenting that the dependency is assumed to already be installed on the
   end user's system, and letting the end user install it themselves (e.g.,
   through their Linux distro package manager).


.. _pip: https://github.com/pypa/pip
.. _pypa/build: https://github.com/pypa/build
.. _Meson: https://github.com/mesonbuild/meson
