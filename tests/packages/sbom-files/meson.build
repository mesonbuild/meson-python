# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('sbom-files', version: '1.0.0')

py = import('python').find_installation()

sboms_dir = get_option('datadir') / meson.project_name() / 'sboms'

# Static SBOM checked into the source tree. It is installed to the
# location matched by the default "tool.meson-python.sbom-files"
# pattern and thus moved to the .dist-info/sboms/ directory in the
# wheel.
install_data('sboms/static.cdx.json', install_dir: sboms_dir)

# SBOM generated at build time.
custom_target('generated-sbom',
  output: 'generated.cdx.json',
  command: [py, files('generate.py'), '@OUTPUT@'],
  install: true,
  install_dir: sboms_dir)

# Regular data file, not matched by the sbom-files patterns.
install_data('data.txt', install_dir: get_option('datadir') / meson.project_name())
