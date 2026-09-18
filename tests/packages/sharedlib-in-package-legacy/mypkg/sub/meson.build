# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

example_lib2 = shared_library(
    'examplelib2',
    'examplelib2.c',
    c_args: export_dll_args,
    install: true,
    install_dir: py.get_install_dir() / 'mypkg/sub',
)

example_lib2_dep = declare_dependency(
    compile_args: import_dll_args,
    link_with: example_lib2,
)
