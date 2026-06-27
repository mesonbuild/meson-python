.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-dynamic-versioning:

******************
Dynamic versioning
******************

The most common approach to versioning is to keep a static version number in
``pyproject.toml`` only, and update it before a new release in a regular commit.
This is simple and robust. However, sometimes a package author may want more
from versioning, and hence reach for dynamic versioning. E.g.:

1. Use the package version in a ``meson.build`` file without duplicating the version string between ``pyproject.toml`` and ``meson.build``.
2. Use the hash of the current commit in the package version, or store it in a configuration file.
3. Derive the version from the most recent git tag rather than maintain it in the code.

.. note::

    Each of these things has a cost - keeping all metadata static and not
    running ``git`` or introspecting the ``.git`` directory as part of the build
    avoids running extra build steps in some cases, extra build dependencies or
    custom scripts, and potential issues with shallow checkouts in CI where the
    ``.git`` directory may not be present. Only use these dynamic features if
    you have a good reason to do so!

Single-sourcing the version string
----------------------------------

When you want to define your project's version string in a single place,
``meson-python`` knows how to extract the version number from the ``project()``
call in the top-level ``meson.build``; in ``pyproject.toml`` it can be declared
as dynamic:

.. code-block:: toml

    [project]
    dynamic = ['version']

Then in ``meson.build``, define the version:

.. code-block:: meson

   project('my-project', 'c', version: '1.2.3')

It can also be done the other way around - this requires a bit more code,
however it has the advantage that all metadata remains static in
``pyproject.toml``, which can in some cases avoid triggering a build
when an installer needs to obtain the version. To implement this,
set the version in ``pyproject.toml``:

.. code-block:: toml

    [project]
    version = '1.2.3'

And in ``meson.build``, run a helper script as part of the project call
(again, this is only needed if you actually use the version string inside a
``meson.build`` file):

.. code-block:: meson

    project('my-project',
        'c',
        version: run_command(
            ['get_version.py'],
            check: true
        ).stdout().strip(),
    )

With that ``get_version.py`` script retrieving the version from
``pyproject.toml``:

.. code-block:: python

    #!/usr/bin/env python3
    import os

    def get_version():
        pyproject_toml = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
        with open(pyproject_toml) as f:
            data = f.readlines()

        version_line = next(
            line for line in data if line.startswith('version =')
        )
        version = version_line.strip().split(' = ')[1]
        return version.replace('"', '').replace("'", '')


    if __name__ == "__main__":
        print(get_version())


Storing the git commit hash inside your package
-----------------------------------------------

Capturing the git commit hash alongside the version can be useful for bug
reports and reproducibility: the user can print ``pkgname.__version__`` and
``pkgname.__git_hash__`` to identify exactly which commit they are running. The
commit hash is not part of ``pyproject.toml`` and cannot be derived from a
source distribution after the fact, so it has to be written into the package at
build time.

A pattern to achieve this, which used by NumPy for example, is a single helper
script that does double duty: it prints the version when called from
``project()``, and it writes a generated ``_version.py`` file containing both
the version and the git hash when called from a build step. The
script is wired up via ``custom_target()`` for normal builds and via
``meson.add_dist_script()`` so that the generated file is also included
in source distributions.

In ``meson.build``:

.. literalinclude:: ../../tests/packages/dynamic-version-from-script/meson.build
   :language: meson
   :lines: 5-

The ``build_always_stale: true`` flag ensures that the recorded hash is
refreshed every time the project is rebuilt, rather than being cached
from a previous build.

The helper script reads the version from ``pyproject.toml`` (so the
version still has a single source of truth) and resolves the git hash
via ``git rev-parse``, falling back to ``'unknown'`` when called outside
a checkout — for example when building from an extracted source
distribution:

.. literalinclude:: ../../tests/packages/dynamic-version-from-script/generate_version.py
   :language: python
   :lines: 1,5-

The ``MESON_DIST_ROOT`` branch ensures that when the script is invoked
as a dist script, it writes the generated file into the staging
directory ``meson dist`` is preparing, so it is included in the source
distribution. See :ref:`sdist` for the surrounding context.

The package's ``__init__.py`` re-exports the generated symbols:

.. code-block:: python

    from pkgname._version import __git_hash__, __version__

A complete worked example lives at ``tests/packages/dynamic-version-from-script``
in the meson-python source tree.


Derive version from latest git tag
----------------------------------

When the version is encoded in git tags rather than in source files, the
build system has to query git at configure time. There are a number of
packages that provide this functionality - e.g., ``setuptools-scm`` as the most
popular one - and that can be used together with ``meson-python``. The
integration principle is the same as above: use a ``run_command()`` call inside
``project()`` (either directly or through a small wrapper script like
``get_version.py`` higher up) that prints the version and (optionally) writes
out a file to disk that can be included in the sdist.

The example below uses ``setuptools-scm``; the same approach applies
to the other tools - only the wrapper script differs. Declare it as a build
requirement in ``pyproject.toml``:


.. literalinclude:: ../../tests/packages/version-setuptools-scm/pyproject.toml
   :language: toml
   :lines: 5-12

In ``meson.build``, invoke ``setuptools-scm`` to compute the version:

.. literalinclude:: ../../tests/packages/version-setuptools-scm/meson.build
   :language: meson
   :lines: 5-

That's it. You can use ``setuptools-scm`` config options as explained in its docs.
If you do want to store a generated file ``.py`` file with versioning metadata,
use ``meson.add_dist_script()`` as explained higher up.
