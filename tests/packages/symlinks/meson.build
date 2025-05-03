# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('symlinks')

py = import('python').find_installation()

py.install_sources(
    '__init__.py',
    'submodule/__init__.py',
    'submodule/aaa.py',
    'submodule/bbb.py',
    subdir: 'symlinks',
    preserve_path: true,
)
