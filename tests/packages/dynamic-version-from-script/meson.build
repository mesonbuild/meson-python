# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project(
    'dynamic-version-from-script',
    version: run_command(['generate_version.py'], check: true).stdout().strip(),
)

fs = import('fs')
py = import('python').find_installation()

py.install_sources(
    'dynamic_version_from_script/__init__.py',
    subdir: 'dynamic_version_from_script',
)

meson.add_dist_script('generate_version.py', 'dynamic_version_from_script/_version.py')

if not fs.exists('dynamic_version_from_script/_version.py')
    custom_target(
        'write_version_file',
        output: '_version.py',
        command: ['generate_version.py', '@OUTPUT@'],
        build_by_default: true,
        build_always_stale: true,
        install: true,
        install_dir: py.get_install_dir() / 'dynamic_version_from_script',
    )
else
    # When building from sdist, _version.py exists and should be included
    py.install_sources(
        ['dynamic_version_from_script/_version.py'],
        subdir: 'dynamic_version_from_script',
    )
endif
