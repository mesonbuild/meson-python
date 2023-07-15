# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('library', 'c', version: '1.0.0')

install_headers('examplelib.h')

example_lib = shared_library(
    'example',
    'examplelib.c',
    install: true,
)

executable(
    'example',
    'example.c',
    link_with: example_lib,
    install: true,
)
