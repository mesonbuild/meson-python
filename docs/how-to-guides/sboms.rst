.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-sboms:

***********************************
Including SBOMs in wheels (PEP 770)
***********************************

`PEP 770`_ defines a standard location for Software Bill of Materials
(SBOM) documents describing the contents of Python packages: the
``sboms/`` subdirectory of the wheel's ``.dist-info/`` directory.

``meson-python`` moves files installed by the Meson project at a
location matching one of the glob patterns in the
:option:`tool.meson-python.sbom-files` setting to the
``.dist-info/sboms/`` directory in the wheel. The default pattern is
``{datadir}/{name}/sboms/*``, with ``{name}`` the normalized project
name: files installed in the ``sboms/`` subdirectory of the project's
data directory are treated as SBOM files. When the Meson project is
installed directly, rather than through a Python build front-end, the
SBOM files are installed in the data directory, alongside the
project's other data files.

.. _PEP 770: https://peps.python.org/pep-0770/

Static SBOM files
=================

SBOM documents checked into the source tree, typically describing
source-vendored components, only need to be installed to the location
matched by the default pattern:

.. code-block:: meson

   project('my-project', 'c', version: '1.0.0')

   install_data(
     'sboms/component1.cdx.json',
     'sboms/component2.cdx.json',
     install_dir: get_option('datadir') / meson.project_name() / 'sboms',
   )

The files end up in the wheel at
``my_project-1.0.0.dist-info/sboms/component1.cdx.json`` and
``component2.cdx.json``.

Dynamically generated SBOMs
===========================

When the SBOM is generated at build time, use a ``custom_target`` that
writes the file and installs it to the same location:

.. code-block:: meson

   py = import('python').find_installation()

   custom_target('vendored-sbom',
     output: 'vendored.cdx.json',
     command: [py, files('scripts/generate_sbom.py'), '@OUTPUT@',
               '--version', meson.project_version()],
     install: true,
     install_dir: get_option('datadir') / meson.project_name() / 'sboms',
   )

The generator is provided by the project; ``meson-python`` does not
ship one. It can be a script checked into the source tree
(``scripts/`` is a common convention) or a third-party generator
installed via ``[build-system] requires``. For guidance on generator
implementations and the SBOM format itself, see the PSF
`SBOMs for Python packages`_ proposal.

Customizing the patterns
========================

The :option:`tool.meson-python.sbom-files` setting accepts a list of
glob patterns matched against the files' installation paths as they
appear in the Meson introspection data:

.. code-block:: toml

   [tool.meson-python]
   sbom-files = ['{datadir}/my-project/sboms/*.cdx.json']

Declaring the setting replaces the default pattern. Setting it to an
empty list disables the special handling of SBOM files entirely.

File naming and validation
==========================

* Files are placed in ``.dist-info/sboms/`` under their file name.
  ``meson-python`` raises an error at build time when two matched
  files have the same name.
* Recommended file extensions are ``.cdx.json`` for CycloneDX and
  ``.spdx.json`` for SPDX, per the PSF `SBOMs for Python packages`_
  proposal.

.. _SBOMs for Python packages: https://github.com/psf/sboms-for-python-packages

Editable installs
=================

SBOM files are only placed in regular wheels (``pip install .`` or
``python -m build``). Editable wheels (``pip install -e .``) redirect
imports to the build directory and do not carry SBOM files. Since
SBOMs are distribution artifacts, this limitation does not affect
development workflows.
