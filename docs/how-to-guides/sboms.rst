.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-sboms:

***********************************
Including SBOMs in wheels (PEP 770)
***********************************

`PEP 770`_ defines a location for Software Bill of Materials (SBOM)
files inside the wheel's ``.dist-info/sboms/`` directory.
``meson-python`` routes any file installed under
``{py_purelib}/<name>-<version>.dist-info/<subdir>/...`` or
``{py_platlib}/<name>-<version>.dist-info/<subdir>/...`` into the
wheel's own ``.dist-info/<subdir>/`` at pack time, giving projects a
way to ship SBOMs and other dist-info-bound metadata files without
post-build wheel surgery.

.. _PEP 770: https://peps.python.org/pep-0770/

Static SBOM files
=================

For SBOMs that are checked into the source tree, typically describing
source-vendored components:

.. code-block:: meson

   project('my-project', 'c', version: '1.0.0')

   py = import('python').find_installation(pure: false)
   distinfo = meson.project_name() + '-' + meson.project_version() + '.dist-info'

   install_data(
     'sboms/component1.cdx.json',
     'sboms/component2.cdx.json',
     install_dir: py.get_install_dir() / distinfo / 'sboms',
   )

The files end up in the wheel at
``my_project-1.0.0.dist-info/sboms/component1.cdx.json`` and
``component2.cdx.json``. ``py.get_install_dir()`` returns a path under
``{py_purelib}`` for ``pure: true`` projects and ``{py_platlib}`` for
``pure: false`` projects; both roots are recognized.

Dynamically generated SBOMs
===========================

When the SBOM is generated at build time, use a ``custom_target`` that
writes the file and installs it to the same location:

.. code-block:: meson

   custom_target('vendored-sbom',
     output: 'vendored.cdx.json',
     command: [py, files('scripts/generate_sbom.py'), '@OUTPUT@',
               '--version', meson.project_version()],
     install: true,
     install_dir: py.get_install_dir() / distinfo / 'sboms',
   )

The generator runs during the build, and the output is routed into
``my_project-1.0.0.dist-info/sboms/vendored.cdx.json``.

Other ``.dist-info`` subdirectories
===================================

Any subdirectory works the same way. Additional PEP 639 license files,
for example, can go under ``licenses``:

.. code-block:: meson

   install_data('LICENSES/extra.txt',
     install_dir: py.get_install_dir() / distinfo / 'licenses')

License files declared via ``project.license-files`` in
``pyproject.toml`` are already placed in ``.dist-info/licenses/``
automatically and do not need a ``meson.build`` entry. Use the pattern
above only for additional files outside the standard
``project.license-files`` list.

File naming and validation
==========================

* Files installed under ``<name>-<version>.dist-info/<subdir>/`` must
  have unique basenames within their subdirectory. ``meson-python``
  raises a ``BuildError`` at build time if two files would write to
  the same path, including collisions between files routed through
  this mechanism and files written from ``project.license-files``.
* The ``<name>-<version>.dist-info`` directory name is matched
  canonically, so hyphens and underscores in the user's project name
  do not break routing.
* Recommended file extensions are ``.cdx.json`` for CycloneDX and
  ``.spdx.json`` for SPDX, per the PSF
  `SBOMs for Python packages`_ proposal.

.. _SBOMs for Python packages: https://github.com/psf/sboms-for-python-packages

Editable installs
=================

Files staged via this mechanism are only placed in non-editable wheels
(``pip install .`` or ``python -m build``). Editable wheels
(``pip install -e .``) redirect imports to the build directory and do
not carry dist-info-bound payloads. Since SBOMs are distribution
artifacts, this limitation does not affect development workflows.
