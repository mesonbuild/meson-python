# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('link-against-local-lib', 'c', version: '1.0.0')

if meson.get_compiler('c').get_id() in ['msvc', 'clang-cl', 'intel-cl']
    lib_compile_args = ['-DEXAMPLE_DLL_EXPORTS']
    link_args = ['-DEXAMPLE_DLL_IMPORTS']
else
    lib_compile_args = []
    link_args = ['-Wl,-rpath,custom-rpath']
endif

subdir('lib')

py = import('python').find_installation(pure: false)

py.install_sources(
    '__init__.py',
    subdir: 'example',
)

py.extension_module(
    '_example',
    'examplemod.c',
    link_with: example_lib,
    link_args: link_args,
    install: true,
    subdir: 'example',
)
