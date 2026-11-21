.. SPDX-FileCopyrightText: 2024 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _sdist:

******************************
Creating a source distribution
******************************

A source distribution for the project can be created executing

.. code-block:: console

   $ python -m build --sdist .

in the project root folder. This will create a ``.tar.gz`` archive in the
``dist`` folder in the project root folder. This archive contains the full
contents of the latest commit in revision control with all revision control
metadata removed. Uncommitted modifications and files unknown to the revision
control system are not included.

The source distribution archive is created by adding the required metadata
files to the archive obtained by executing the ``meson dist --no-tests
--allow-dirty`` command. To generate a source distribution, ``meson-python``
must successfully configure the Meson project by running the ``meson setup``
command. Additional arguments can be passed to ``meson dist`` to alter its
behavior. Refer to the relevant `Meson documentation`__ and to the
:ref:`how-to-guides-meson-args` guide for details.

The ``meson dist`` command uses the archival tool of the underlying revision
control system for creating the archive. This implies that a source
distribution can only be created for a project versioned in a revision control
system. Meson supports the Git and Mercurial revision control systems.

Files can be excluded from the source distribution via the relevant mechanism
provided by the revision control system. When using Git as a revision control
system, it is possible to exclude files from the source distribution setting
the ``export-ignore`` attribute. For example, adding a ``.gitattributes``
files containing

.. code-block:: none

   dev/** export-ignore

would result in the ``dev`` folder to be excluded from the source
distribution. Refer to the ``git archive`` documentation__ for
details. Another mechanism to alter the content of the source distribution is
offered by dist scripts. Refer to the relevant `Meson documentation`__ for
details.

__ https://mesonbuild.com/Creating-releases.html
__ https://git-scm.com/docs/git-archive#ATTRIBUTES
__ https://mesonbuild.com/Reference-manual_builtin_meson.html#mesonadd_dist_script

Packaging Python bindings from a subdirectory
=============================================

A C or C++ library can keep its Python bindings in a separate Meson project.
For example, the following repository can build the C library at its root with
``meson setup build`` and ``meson compile -C build``. The Python package has
its own ``pyproject.toml`` and can be built from ``python/``.

.. code-block:: text

   meson.build
   src/example.c
   src/example.h
   python/
       pyproject.toml
       meson.build
       examplemodule.c
       prepare_sdist.py
       subprojects/
           examplelib -> ../..

The library exposes a dependency that the Python extension can link against.
It is built statically here so the wheel only needs to install the extension.
The root ``meson.build`` also installs the library when built independently.

.. literalinclude:: ../../tests/packages/native-library/meson.build
   :language: meson
   :lines: 5-

In a checkout, point ``python/subprojects/examplelib`` at the library root.
From the root, run ``ln -s ../.. python/subprojects/examplelib``. On Windows,
a directory junction can be created from Command Prompt with
``mklink /J python\subprojects\examplelib "%CD%"``. Ignore this local link
in ``python/subprojects/.gitignore`` by adding ``/examplelib``.

The bindings get the dependency from this local subproject and register a
script to run when Meson creates the Python source distribution:

.. literalinclude:: ../../tests/packages/native-library/python/meson.build
   :language: meson
   :lines: 5-

Meson archives the ``python/`` subtree. The local link and the native sources
above it are therefore absent from that archive. The dist script supplies a
regular ``subprojects/examplelib`` directory with the files needed to build
the library. If the staging directory contains a tracked symlink, the script
removes it before writing the files. Reading the committed native sources from
Git keeps local edits out of the sdist.

.. literalinclude:: ../../tests/packages/native-library/python/prepare_sdist.py
   :language: python
   :lines: 5-

Run ``python -m build --wheel python`` to build directly from the checkout.
Run ``python -m build python`` to create the sdist and build a wheel from it.
The extracted sdist includes the local subproject and builds without Git or
a separate copy of the library.
