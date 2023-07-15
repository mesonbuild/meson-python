# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('executable-bit', 'c', version: '1.0.0')

fs = import('fs')
py = import('python').find_installation()

executable(
    'example',
    'example.c',
    install: true,
)

install_data(
    'example-script.py',
    rename: 'example-script',
    install_dir: get_option('bindir'),
)

py.install_sources('executable_module.py')

version_gen = files('generate_version.py')

if fs.exists('_version_meson.py')
    py.install_sources('_version_meson.py')
else
    custom_target(
        'write_version_file',
        output: '_version_meson.py',
        command: [py, version_gen, '-o', '@OUTPUT@'],
        build_by_default: true,
        build_always_stale: true,
        install: true,
        install_dir: py.get_install_dir(pure: false),
    )
    meson.add_dist_script(py, version_gen, '-o', '_version_meson.py')
endif
