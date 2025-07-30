# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

py.extension_module(
    '_example',
    '_examplemod.c',
    dependencies: lib_dep,
    install: true,
    subdir: 'mypkg',
    # install_rpath is not exposed in the Meson introspection data in Meson
    # versions prior to 1.6.0 and thus cannot be set by meson-python when
    # building the Python wheel. Use link_args to set the RPATH.
    # install_rpath: '$ORIGIN',
    link_args: '-Wl,-rpath,$ORIGIN',
)

py.install_sources(
    ['__init__.py'],
    subdir: 'mypkg',
)
