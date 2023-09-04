# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('purelib-and-platlib', 'c', version: '1.0.0')

py = import('python').find_installation()

py.install_sources(
    'pure.py',
    install_tag: 'purelib',
)

py.extension_module(
    'plat',
    'plat.c',
    install: true,
    install_tag: 'platlib',
)
