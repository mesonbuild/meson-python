# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('detect-compiler', 'c', version: '1.0')

py = import('python').find_installation()

py.extension_module('detect_compiler', 'detect_compiler.c', install: true)
