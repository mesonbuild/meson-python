# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('link-against-local-lib', 'c', version: '1.0.0')

example_lib = shared_library(
    'example',
    'examplelib.c',
    install: true,
)

py = import('python').find_installation()

py.extension_module(
    'example',
    'examplemod.c',
    link_with: example_lib,
    link_args: ['-Wl,-rpath,custom-rpath'],
    install: true,
)
