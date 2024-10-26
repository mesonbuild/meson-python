.. SPDX-FileCopyrightText: 2022 The meson-python developers
..
.. SPDX-License-Identifier: MIT

:hide-toc:

************
meson-python
************

.. highlights::

  A Python package build backend leveraging the Meson build system.

``meson-python`` implement the Python build system hooks, enabling Python build
front-ends such as ``pip`` and ``build`` to build and install Python packages
based on a Meson_ build definition.

Meson is characterized by build definitions written in a very readable
domain-specific language and extremely fast builds.  Meson support for Windows,
macOS, Linux, and other UNIX-like operative systems, and for all the major
compiler tool-chains. It allows to compile and link together code written in
many programming languages, including C, C++, Cython, D, Fortran, Objective C,
and Rust. It has built-in multi-platform dependency provider that works well
with distribution packages, and the capability to build dependencies as
sub-projects.  If you are not familiar with Meson, we recommend checking the
`Meson tutorial`_.

``meson-python`` inherits the strengths of Meson and is thus best suited for
Python packages building extension modules in compiled languages.
``meson-python`` is suitable for small packages as well as very complex ones,
see our :ref:`projects-using-meson-python` directory.

To enable ``pip`` or ``build`` to build a Python source distribution (*sdist*)
or a binary Python package (*wheel*) for a Meson project, it is sufficient to
add to the root of the source tree next to the top-level ``meson.build`` a
``pyproject.toml`` file specifying ``meson-python`` as the Python build
backend:

.. code-block:: toml

   [build-system]
   build-backend = 'mesonpy'
   requires = ['meson-python']

The package name and version are extracted from the metadata provided to Meson
via the ``project()`` function in the ``meson.build`` file.  Package metadata
can be overridden and extended using the standard package metadata format in the
``project`` section of ``pyproject.toml``:

.. code-block:: toml

   [project]
   name = 'example'
   version = '1.0.0'
   description = 'Example package using the meson-python build backend'
   readme = 'README.rst'
   license = {file = 'LICENSE.txt'}
   authors = [
     {name = 'Au Thor', email = 'author@example.com'},
   ]

   [project.scripts]
   example = 'example.cli:main'

Please refer to the `PyPA documentation`_ for detailed documentation about the
``pyproject.toml`` file.  Please refer to our :ref:`tutorial` for guidance about
the use of ``meson-python`` and Meson for Python packaging.


.. _Meson: https://mesonbuild.com/
.. _PyPA documentation: https://packaging.python.org/en/latest/specifications/declaring-project-metadata/
.. _Meson tutorial: https://mesonbuild.com/Tutorial.html


.. toctree::
   :hidden:

   tutorials/introduction
   how-to-guides/sdist
   how-to-guides/editable-installs
   how-to-guides/config-settings
   how-to-guides/meson-args
   how-to-guides/debug-builds
   how-to-guides/shared-libraries
   reference/limitations
   projects-using-meson-python

.. toctree::
   :caption: Reference
   :hidden:

   reference/config-settings
   reference/pyproject-settings
   reference/environment-variables
   explanations/default-options
   reference/meson-compatibility

.. toctree::
   :caption: Project
   :hidden:

   changelog
   about
   Discussions <https://github.com/mesonbuild/meson-python/discussions>
   Source Code <https://github.com/mesonbuild/meson-python>
   Issue Tracker <https://github.com/mesonbuild/meson-python/issues>
