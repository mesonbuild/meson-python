# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import subprocess

import pytest

import mesonpy


ninja_ver_str = subprocess.run(['ninja', '--version'], check=True, stdout=subprocess.PIPE, text=True).stdout
NINJA_VERSION = tuple(map(int, ninja_ver_str.split('.')[:3]))


# Ninja 1.9 does not support the soruce^ syntax to specify a target.
@pytest.mark.skipif(NINJA_VERSION < (1, 10), reason='Ninja version too old')
@pytest.mark.parametrize(
    ('args', 'expected'),
    [
        ([], True),
        (['-Dbuildtype=release'], True),
        (['-Dbuildtype=debug'], False),
    ],
    ids=['', '-Dbuildtype=release', '-Dbuildtype=debug'],
)
def test_ndebug(package_purelib_and_platlib, tmp_path, args, expected):
    with mesonpy._project({'setup-args': args}) as project:
        command = subprocess.run(
            # Ask ninja what is the command that would be used to
            # compile a C source file (the trailing ^ is used to
            # specify the target that is the first output of the rule
            # containing the specified source file).
            ['ninja', '-C', os.fspath(project._build_dir), '-t', 'commands', '../plat.c^'],
            stdout=subprocess.PIPE, check=True).stdout
        assert (b'-DNDEBUG' in command) == expected
