# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('purelib-platlib-split', version: '1.0.0')

py = import('python').find_installation()

py.install_sources(
    'pure.py',
    subdir: 'purelib-platlib-split',
)

py.install_sources(
    'plat.py',
    subdir: 'purelib-platlib-split',
    pure: false,
)
