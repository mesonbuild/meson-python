# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('link-against-external-lib', 'c', version: '1.0.0')

py = import('python').find_installation(pure: false)

external = dependency('geos', method: 'pkg-config')

py.extension_module(
    'external',
    'external.c',
    dependencies: external,
    install: true
)
