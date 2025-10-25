# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('package', version: '1.0.0')

py = import('python').find_installation()

py.install_sources(
    '__init__.py',
    subdir: 'package',
)

install_data(
    'data.txt',
    install_dir: py.get_install_dir() / 'package',
)

custom_target(
    output: 'uuid.txt',
    command: [py, '-m', 'uuid'],
    capture: true,
    install: true,
    install_dir: py.get_install_dir() / 'package',
)
