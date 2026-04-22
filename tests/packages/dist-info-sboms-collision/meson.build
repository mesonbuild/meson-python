# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('dist-info-sboms-collision', version: '1.0.0', meson_version: '>=1.12.0')

py = import('python').find_installation()

# This install_data targets the same wheel path as the PEP 639
# license-files entry in pyproject.toml (.dist-info/licenses/LICENSE.txt).
# meson-python should surface the collision as a BuildError rather than
# silently clobber.
install_data('duplicate/LICENSE.txt',
  install_dir: py.dist_info_install_dir('licenses'))
