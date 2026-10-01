# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

subdir('leaf')
subdir('middle')

py.install_sources('__init__.py', subdir: 'chainhead')

py.extension_module(
    'chain', 'module.c',
    link_with: middle,
    install: true,
    subdir: 'chainhead',
    install_rpath: '$ORIGIN/lib',
)
