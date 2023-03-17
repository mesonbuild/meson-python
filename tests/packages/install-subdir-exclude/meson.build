# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('install-subdir-exclude', version: '1.0.0')

py = import('python').find_installation()
purelib = py.get_install_dir(pure: true)

# We need two foo directories because of a bug in the Meson metadata generation.
# https://github.com/mesonbuild/meson/issues/11539

# Examples removed from https://mesonbuild.com/Reference-manual_functions.html#install_subdir
install_subdir(
  'foo',
  install_dir: purelib / 'subdir1',
  strip_directory : false,
)
install_subdir(
  'foo2',
  install_dir: purelib / 'subdir2',
  strip_directory : true,
)
install_subdir(
  'foo/bar',
  install_dir: purelib / 'subdir3',
  strip_directory : false,
)
install_subdir(
  'foo2/bar',
  install_dir: purelib / 'subdir4',
  strip_directory : true,
)
install_subdir(
  'new_directory',
  install_dir: purelib,
)

# Exercise exclude_* options
install_subdir(
  'exclude',
  install_dir: purelib,
  exclude_directories: ['subdir2', 'subdir3'],
  exclude_files: ['file2', 'file3', 'subdir1/file2', 'subdir1/file3'],
)
