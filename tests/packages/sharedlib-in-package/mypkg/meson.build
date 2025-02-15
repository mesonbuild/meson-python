# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

py.extension_module(
    '_example',
    '_examplemod.c',
    dependencies: lib_dep,
    install: true,
    subdir: 'mypkg',
    install_rpath: '$ORIGIN',
)

py.install_sources(
    ['__init__.py'],
    subdir: 'mypkg',
)
