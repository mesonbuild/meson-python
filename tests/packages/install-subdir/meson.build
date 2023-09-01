# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('install-subdir', version: '1.0.0')

py = import('python').find_installation()

install_subdir(
  'subdir',
  exclude_files: 'excluded.py',
  exclude_directories: 'excluded',
  install_dir: py.get_install_dir(pure: false),
)

install_subdir(
  'strip',
  strip_directory: true,
  exclude_files: 'excluded.py',
  install_dir: py.get_install_dir(pure: false) / 'test',
)

install_subdir(
  'nested',
  exclude_files: 'deep/excluded.py',
  install_dir: py.get_install_dir(pure: false),
)
