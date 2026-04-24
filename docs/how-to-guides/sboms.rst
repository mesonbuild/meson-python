.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-sboms:

***********************************
Including SBOMs in wheels (PEP 770)
***********************************

`PEP 770`_ specifies that wheels may carry Software Bill of Materials
(SBOM) documents under the ``.dist-info/sboms/`` directory.
``meson-python`` places any file installed under
``{py_purelib}/<distname>-<version>.dist-info/<subdir>/...`` into the
wheel's ``.dist-info/<subdir>/`` at pack time. This is the mechanism
scientific-Python projects (pandas, NumPy, SciPy, scikit-learn) use to
ship SBOMs in their wheels without post-build wheel surgery.

The ``<distname>-<version>.dist-info`` directory name is recognised
regardless of whether the user wrote the project name with hyphens or
underscores — the comparison is canonicalised.

.. _PEP 770: https://peps.python.org/pep-0770/

Static SBOM files
=================

For SBOMs that are checked into the source tree (typically describing
source-vendored components):

.. code-block:: meson

   project('my-project', 'c', version: '1.0.0')

   py = import('python').find_installation(pure: false)
   distinfo = meson.project_name() + '-' + meson.project_version() + '.dist-info'

   install_data(
     'sboms/component1.cdx.json',
     'sboms/component2.cdx.json',
     install_dir: py.get_install_dir() / distinfo / 'sboms',
   )

``py.get_install_dir()`` returns a path under ``{py_purelib}`` for
``pure: true`` projects and ``{py_platlib}`` for ``pure: false``
(the common case when shipping C extensions). ``meson-python``
recognises the distinfo prefix under either root.

The files end up in the wheel at
``my_project-1.0.0.dist-info/sboms/component1.cdx.json`` and
``component2.cdx.json``.

Dynamically generated SBOMs
===========================

Many projects generate the SBOM at build time from a TOML manifest of
vendored components. Use a ``custom_target`` that produces the SBOM file
and installs it to the same location:

.. code-block:: meson

   custom_target('vendored-sbom',
     output: 'vendored.cdx.json',
     command: [py, files('scripts/generate_sbom.py'), '@OUTPUT@',
               '--version', meson.project_version()],
     install: true,
     install_dir: py.get_install_dir() / distinfo / 'sboms',
   )

The generator runs during the build, and ``meson-python`` injects the
output into ``my_project-1.0.0.dist-info/sboms/vendored.cdx.json``.

Other ``.dist-info`` subdirectories
===================================

Any subdirectory under the ``.dist-info`` directory works the same way.
PEP 639 license files can be placed under ``licenses``, for example:

.. code-block:: meson

   install_data('LICENSES/extra.txt',
     install_dir: py.get_install_dir() / distinfo / 'licenses')

PEP 639 license files declared via ``project.license-files`` in
``pyproject.toml`` are handled separately and go into
``.dist-info/licenses/`` automatically (no ``meson.build`` change
needed). Use the pattern above only for additional license files
outside the standard ``project.license-files`` list.

File naming and validation
==========================

* Files installed under ``<distname>-<version>.dist-info/<subdir>/``
  must have unique basenames within their subdirectory. ``meson-python``
  raises an error at build time if two files would write to the same
  path inside ``.dist-info/<subdir>/``. The collision check covers
  files routed via this mechanism and PEP 639 license-files from
  ``project.license-files``.
* The recommended file extensions are ``.cdx.json`` for CycloneDX and
  ``.spdx.json`` for SPDX, per the PSF
  `SBOMs for Python packages`_ proposal.

.. _SBOMs for Python packages: https://github.com/psf/sboms-for-python-packages

Editable installs
=================

Files staged via this mechanism are placed in the wheel when
``meson-python`` builds a regular wheel (``pip install .`` or
``python -m build``). They are **not** included in editable wheels
(``pip install -e .``), because editable wheels redirect imports to the
build directory rather than carrying project files. SBOMs are intended
for distribution artefacts, so this limitation generally does not
affect development workflows.
