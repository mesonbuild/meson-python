# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('limited-api-free-thraded', 'c', version: '1.0.0', meson_version: '>= 1.3')

py = import('python').find_installation(pure: false)

py.extension_module(
    'module',
    'module.c',
    limited_api: '3.15',
    install: true,
)
