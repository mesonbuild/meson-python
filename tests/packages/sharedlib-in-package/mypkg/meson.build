# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

# install_rpath is not exposed in the Meson introspection data in
# Meson versions prior to 1.6.0 and thus cannot be set by meson-python
# when building the Python wheel. Use link_args to set the RPATH when
# using older Meson.
kwargs = meson.version().version_compare('< 1.6') ? {'link_args': f'-Wl,-rpath,@origin@'} : {'install_rpath': f'@origin@'}

py.extension_module(
    '_example',
    '_examplemod.c',
    dependencies: lib_dep,
    install: true,
    subdir: 'mypkg',
    kwargs: kwargs,
)

py.install_sources(
    ['__init__.py'],
    subdir: 'mypkg',
)
