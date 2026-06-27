# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project(
    'version-setuptools-scm',
    version: run_command(
        ['python3', '-m', 'setuptools_scm'],
        check: true,
    ).stdout().strip(),
)
