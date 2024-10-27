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

example_lib = shared_library(
    'examplelib',
    'examplelib.c',
    c_args: export_dll_args,
    install: true,
    install_dir: py.get_install_dir() / 'mypkg',
)

example_lib_dep = declare_dependency(
    compile_args: import_dll_args,
    link_with: example_lib,
)

subdir('sub')

py.extension_module(
    '_example',
    '_examplemod.c',
    dependencies: [example_lib_dep, example_lib2_dep],
    include_directories: 'sub',
    install: true,
    subdir: 'mypkg',
    install_rpath: '$ORIGIN',
)

py.install_sources(
    ['__init__.py'],
    subdir: 'mypkg',
)
