# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('bar', 'c', version: '1.2.3', meson_version: '>= 1.3.0')

if get_option('default_library') == 'shared' and meson.get_compiler('c').get_id() in ['msvc', 'clang-cl', 'intel-cl']
    export_dll_args = ['-DBAR_DLL_EXPORTS']
    import_dll_args = ['-DBAR_DLL_IMPORTS']
else
    export_dll_args = []
    import_dll_args = []
endif

example_lib = library(
    'examplelib',
    'examplelib.c',
    c_shared_args: export_dll_args,
    install: true,
)

# A second library that we don't link from `foo`. If we install the subproject,
# this second library also ends up in the wheel. To prevent that, we need to
# skip installing this `bar` subproject, and statically link `example_lib`.
unwanted_lib = library(
    'unwantedlib',
    'examplelib.c',
    c_shared_args: export_dll_args,
    install: true,
)

bar_dep = declare_dependency(
    compile_args: import_dll_args,
    link_with: example_lib,
    include_directories: '.',
)
