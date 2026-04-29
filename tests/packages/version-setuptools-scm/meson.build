# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project(
    'version-setuptools-scm',
    version: run_command(
        [find_program('python3', 'python'), '-m', 'setuptools_scm'],
        check: true,
    ).stdout().strip(),
)
