import os
import subprocess

import pytest

import mesonpy


@pytest.mark.parametrize('args', [[], ['-Dbuildtype=release']], ids=['defaults', '-Dbuildtype=release'])
def test_ndebug(package_scipy_like, tmp_path, args):
    with mesonpy._project({'setup-args': args}) as project:
        command = subprocess.run(
            ['ninja', '-C', os.fspath(project._build_dir), '-t', 'commands', '../../mypkg/extmod.c^'],
            stdout=subprocess.PIPE, check=True).stdout
        assert b'-DNDEBUG' in command
