# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

middle = shared_library(
    'middle', 'middle.c',
    link_with: leaf,
    install: true,
    install_dir: py.get_install_dir() / 'chainhead/lib',
)
