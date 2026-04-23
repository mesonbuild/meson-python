# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('dist-info-sboms', version: '1.0.0', meson_version: '>=1.12.0')

py = import('python').find_installation()

# Static SBOM file installed via the helper.
install_data('sboms/static.cdx.json',
  install_dir: py.dist_info_install_dir('sboms'))

# Dynamic SBOM produced by a custom_target. This is the pattern
# scientific-Python projects (pandas, NumPy, SciPy) use to inject
# build-time-generated SBOMs into the wheel.
custom_target('generated-sbom',
  output: 'generated.cdx.json',
  command: [py, files('generate.py'), '@OUTPUT@'],
  install: true,
  install_dir: py.dist_info_install_dir('sboms'))

# Different subdirectory — proves the helper's parameterization works
# and that files routed to two subdirs land in distinct wheel paths.
# 'extras' (rather than 'licenses') avoids suggesting this is a PEP 639
# alternative; PEP 639 license-files still flow through
# pyproject_metadata + the existing _wheel_write_metadata path.
install_data('sboms/extra.txt',
  install_dir: py.dist_info_install_dir('extras'))
