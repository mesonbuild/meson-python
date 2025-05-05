# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('symlinks')

py = import('python').find_installation()

# Note that `baz.py` and `qux.py`, which contain symlinks to outside the repo
# (unsupported), are present in the git repo but won't be present in a
# meson-python sdist (see gh-747).
py.install_sources(
    '__init__.py',
    'submodule/__init__.py',
    'submodule/aaa.py',
    'submodule/bbb.py',
    subdir: 'symlinks',
    preserve_path: true,
)
