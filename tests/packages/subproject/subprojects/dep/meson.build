# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('dep')

py = import('python').find_installation()

py.install_sources(
    'dep.py',
)

install_data(
    'data.txt',
    # Prior to meson 1.3.0, the default install path for subproject data files
    # is ``{datadir}/{main-project-name}/``. In later versions it is the more
    # correct ``{datadir}/{subproject-name}/``. Specify the install path to
    # obtain uniform behavior across different meson versions.
    install_dir: '{datadir}' / meson.project_name(),
)
