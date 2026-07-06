# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('sbom-files-collision', version: '1.0.0')

# Both files match a "tool.meson-python.sbom-files" pattern and have
# the same name: moving both to .dist-info/sboms/ must raise an error.
install_data('a/dup.cdx.json', install_dir: get_option('datadir') / 'a')
install_data('b/dup.cdx.json', install_dir: get_option('datadir') / 'b')
