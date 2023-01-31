# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

project(
    'purelib-and-platlib', 'c',
    version: '1.0.0',
)

py_mod = import('python')
py = py_mod.find_installation()

py.install_sources('pure.py')
py.extension_module(
    'plat', 'plat.c',
    install: true,
)
