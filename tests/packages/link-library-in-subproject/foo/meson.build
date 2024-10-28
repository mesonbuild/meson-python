# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

py.extension_module(
    '_example',
    '_examplemod.c',
    dependencies: bar_dep,
    install: true,
    subdir: 'foo',
)

py.install_sources(
    ['__init__.py'],
    subdir: 'foo',
)
