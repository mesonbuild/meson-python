# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project(
    'version-vcs-versioning',
    version: run_command(
        [find_program('python3', 'python'), '-m', 'vcs_versioning'],
        check: true,
    ).stdout().strip(),
)
