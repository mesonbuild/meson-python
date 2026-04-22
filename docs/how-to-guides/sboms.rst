.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-sboms:

***********************************
Including SBOMs in wheels (PEP 770)
***********************************

`PEP 770`_ specifies that wheels may carry Software Bill of Materials
(SBOM) documents under the ``.dist-info/sboms/`` directory. ``meson-python``
supports placing arbitrary files into the ``.dist-info/<subdir>/`` of the
generated wheel via the
``python.dist_info_install_dir()`` helper introduced in Meson 1.12.0.

This page walks through the static and dynamic patterns that scientific
Python projects (pandas, NumPy, SciPy, scikit-learn) use to ship SBOMs
in their wheels.

.. _PEP 770: https://peps.python.org/pep-0770/

Static SBOM files
=================

For SBOMs that are checked into the source tree (typically describing
source-vendored components):

.. code-block:: meson

   project('my-project', version: '1.0.0', meson_version: '>=1.12.0')

   py = import('python').find_installation()

   install_data(
     'sboms/component1.cdx.json',
     'sboms/component2.cdx.json',
     install_dir: py.dist_info_install_dir('sboms'),
   )

The files end up in the wheel at
``my_project-1.0.0.dist-info/sboms/component1.cdx.json`` and
``component2.cdx.json``.

Dynamically generated SBOMs
===========================

Many projects generate the SBOM at build time from a TOML manifest of
vendored components. Use a ``custom_target`` that produces the SBOM file
and installs it via the same helper:

.. code-block:: meson

   custom_target('vendored-sbom',
     output: 'vendored.cdx.json',
     command: [py, files('scripts/generate_sbom.py'), '@OUTPUT@',
               '--version', meson.project_version()],
     install: true,
     install_dir: py.dist_info_install_dir('sboms'),
   )

The generator runs during the build, and ``meson-python`` injects the
output into ``my_project-1.0.0.dist-info/sboms/vendored.cdx.json``.

Other ``.dist-info`` subdirectories
===================================

The same helper accepts any subdirectory name. PEP 639 license files
land in ``licenses``, for example:

.. code-block:: meson

   install_data('LICENSES/extra.txt',
     install_dir: py.dist_info_install_dir('licenses'))

PEP 639 license files declared via ``project.license-files`` in
``pyproject.toml`` are handled separately (no ``meson.build`` change
needed). Use ``dist_info_install_dir('licenses')`` only for additional
license files outside the standard ``project.license-files`` list.

File naming and validation
==========================

* Files installed via ``dist_info_install_dir()`` must have unique
  basenames within their subdirectory. ``meson-python`` will raise an
  error at build time if two files would write to the same path inside
  ``.dist-info/<subdir>/``.
* The recommended file extensions are ``.cdx.json`` for CycloneDX and
  ``.spdx.json`` for SPDX, per the PSF
  `SBOMs for Python packages`_ proposal.

.. _SBOMs for Python packages: https://github.com/psf/sboms-for-python-packages

Editable installs
=================

Files installed via ``dist_info_install_dir()`` are placed in the wheel
when ``meson-python`` builds a regular wheel (``pip install .`` or
``python -m build``). They are **not** included in editable wheels
(``pip install -e .``), because editable wheels redirect imports to the
build directory rather than carrying project files. SBOMs are intended
for distribution artefacts, so this limitation generally does not affect
development workflows.
