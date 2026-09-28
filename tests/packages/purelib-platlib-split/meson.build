# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('purelib-platlib-split', version: '1.0.0')

py = import('python').find_installation()

install_subdir(
    'pure',
    strip_directory: true,
    exclude_files: get_option('empty') == 'pure' ? ['pure.py'] : [],
    install_dir: py.get_install_dir() / 'purelib-platlib-split',
)

install_subdir(
    'plat',
    strip_directory: true,
    exclude_files: get_option('empty') == 'plat' ? ['plat.py'] : [],
    install_dir: py.get_install_dir(pure: false) / 'purelib-platlib-split',
)
