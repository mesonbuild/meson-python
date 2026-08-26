# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('sbom-files-custom', version: '1.0.0')

# Matched by the "tool.meson-python.sbom-files" pattern declared in
# pyproject.toml and thus moved to .dist-info/sboms/ in the wheel.
install_data('sboms/custom.cdx.json', install_dir: get_option('datadir') / 'custom')

# Not matched: setting "tool.meson-python.sbom-files" replaces the
# default pattern, thus files installed to the default location are
# not treated specially anymore.
install_data('sboms/other.cdx.json',
  install_dir: get_option('datadir') / meson.project_name() / 'sboms')

# Not matched: does not match the *.cdx.json glob.
install_data('sboms/readme.txt', install_dir: get_option('datadir') / 'custom')
