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

# The two install_subdir() below are used to verify package split checks in
# presence of install_subdir() that do not result in any file added to the
# wheel.

# Due to the exclude_files argument, this install_subdir() does not result
# into any file installed, however, this is supported only with Meson 1.1.0
# and later.  For simplicity, leave it out on older Meson versions.
if meson.version().version_compare('>= 1.1')
    install_subdir(
        'purelib',
        strip_directory: true,
        exclude_files: 'excluded.py',
        install_dir: py.get_install_dir(pure: true) / 'example',
    )
endif

install_subdir(
    'platlib',
    strip_directory: true,
    install_dir: py.get_install_dir(pure: false) / 'example',
)
