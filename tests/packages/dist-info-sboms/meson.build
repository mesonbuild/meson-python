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

# Different subdirectory — proves the helper's parameterization works.
install_data('sboms/license-extra.txt',
  install_dir: py.dist_info_install_dir('licenses'))
