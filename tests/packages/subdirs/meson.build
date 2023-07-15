# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('subdirs', version: '1.0.0')

py = import('python').find_installation()

# in Meson >= 0.64 this could be replace with a single
# py.install_sources() with the 'preserve_path: true' argument.
py.install_sources(
    'subdirs/__init__.py',
    subdir: 'subdirs',
)

py.install_sources(
    'subdirs/a/__init__.py',
    subdir: 'subdirs/a',
)

py.install_sources(
    'subdirs/a/b/c.py',
    subdir: 'subdirs/a/b',
)

py.install_sources(
    'subdirs/b/c.py',
    subdir: 'subdirs/b',
)
