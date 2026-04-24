# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('dist-info-sboms', version: '1.0.0')

py = import('python').find_installation()

# Compose the wheel's .dist-info/ directory name. meson-python detects
# this prefix under {py_purelib}/... in the install plan and routes the
# file into the wheel's own .dist-info/.
distinfo = meson.project_name() + '-' + meson.project_version() + '.dist-info'

# Static SBOM file.
install_data('sboms/static.cdx.json',
  install_dir: py.get_install_dir() / distinfo / 'sboms')

# Dynamic SBOM produced by a custom_target. This is the pattern
# scientific-Python projects (pandas, NumPy, SciPy) use to inject
# build-time-generated SBOMs into the wheel.
custom_target('generated-sbom',
  output: 'generated.cdx.json',
  command: [py, files('generate.py'), '@OUTPUT@'],
  install: true,
  install_dir: py.get_install_dir() / distinfo / 'sboms')

# Different subdirectory — proves the routing handles arbitrary
# subdir names, not just 'sboms'. 'extras' (rather than 'licenses')
# avoids suggesting this is a PEP 639 alternative; PEP 639
# license-files still flow through pyproject_metadata + the existing
# _wheel_write_metadata path.
install_data('sboms/extra.txt',
  install_dir: py.get_install_dir() / distinfo / 'extras')
