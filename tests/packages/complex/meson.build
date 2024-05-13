# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('complex', 'c', 'cython', version: '1.0.0')

# Work around Python bug on mingw-w64, fixed in Python 3.12
# https://github.com/python/cpython/pull/100137
# The same work-around is also included in Meson 1.1.0 and later.
if meson.version().version_compare('< 1.1')
    if host_machine.system() == 'windows' and meson.get_compiler('c').get_id() == 'gcc'
        add_project_arguments('-DMS_WIN64=', language: 'c')
    endif
endif

py = import('python').find_installation()

py.install_sources(
    'move.py',
    subdir: 'complex/more',
    pure: false,
)

install_data(
    'foo.py',
    rename: 'bar.py',
    install_dir: py.get_install_dir(pure: false) / 'complex',
)

install_subdir(
    'complex',
    install_dir: py.get_install_dir(pure: false),
    exclude_files: ['more/meson.build', 'more/baz.pyx'],
)

py.extension_module(
    'extension',
    'extension.c',
    install: true,
    subdir: 'complex',
)

py.extension_module(
    'test',
    'test.pyx',
    install: true,
    subdir: 'complex',
)

py.extension_module(
    'baz',
    'complex/more/baz.pyx',
    install: true,
    subdir: 'complex/more',
)

subdir('complex/more')
