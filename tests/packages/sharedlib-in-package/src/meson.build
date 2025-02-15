# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

if meson.get_compiler('c').get_id() in ['msvc', 'clang-cl', 'intel-cl']
    export_dll_args = ['-DMYPKG_DLL_EXPORTS']
    import_dll_args = ['-DMYPKG_DLL_IMPORTS']
else
    export_dll_args = []
    import_dll_args = []
endif

sublib = shared_library(
    'sublib',
    'sublib.c',
    c_args: export_dll_args,
    install: true,
    install_dir: py.get_install_dir() / 'mypkg/sub',
)

sublib_dep = declare_dependency(
    compile_args: import_dll_args,
    link_with: sublib,
)

lib = shared_library(
    'lib',
    'lib.c',
    dependencies: sublib_dep,
    c_args: export_dll_args,
    install: true,
    install_dir: py.get_install_dir() / 'mypkg',
    install_rpath: '$ORIGIN/sub',
)

lib_dep = declare_dependency(
    compile_args: import_dll_args,
    link_with: lib,
    include_directories: include_directories('.'),
)
