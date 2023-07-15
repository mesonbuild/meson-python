# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('executable-bit', 'c', version: '1.0.0')

py = import('python').find_installation()

executable(
    'example',
    'example.c',
    install: true,
)

install_data(
    'example-script.py',
    rename: 'example-script',
    install_dir: get_option('bindir'),
)

py.install_sources('executable_module.py')
