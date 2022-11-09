import platform
import subprocess
import sys

import pytest

from .conftest import build_project_wheel, examples_dir


# This test fails on Ubuntu and MacOS for pypy-3.8;
# see https://github.com/mesonbuild/meson-python/pull/136 for more information.
@pytest.mark.skipif(platform.system() != 'Linux', reason='Unsupported on this platform for now')
@pytest.mark.skipif(sys.version_info < (3, 8), reason='Example only supports >=3.8')
def test_build_and_import(venv, tmp_dir_session):
    """Test that the wheel for the spam example builds, installs, and imports."""
    wheel = build_project_wheel(
        package=examples_dir / 'spam',
        outdir=tmp_dir_session
    )

    subprocess.check_call([
        venv.executable, '-m', 'pip', '--disable-pip-version-check', 'install', wheel
    ])
    output, status = subprocess.check_output([
        venv.executable, '-c', f'import spam; print(spam.system("ls {wheel}"))'
    ]).decode().strip().split('\n')

    assert output == str(wheel)
    assert int(status) == 0
