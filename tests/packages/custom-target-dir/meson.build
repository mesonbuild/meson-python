# SPDX-FileCopyrightText: 2024 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('custom-target-dir', version: '1.0.0')

py = import('python').find_installation()

custom_target(
    command: ['codegen.py', '@OUTDIR@'],
    output: 'generated',
    install: true,
    install_dir: py.get_install_dir() / 'package',
)
