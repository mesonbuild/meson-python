import pathlib
import subprocess
import sys

import pytest

import mesonpy

from mesonpy._util import chdir


examples_dir = pathlib.Path(__file__).parent.parent / 'docs' / 'examples'


def test_spam(venv, tmp_path):
    """Test that the wheel for the example builds, installs, and imports."""
    with chdir(examples_dir / 'spam'):
        if sys.version_info < (3, 8):
            # The test project requires Python >= 3.8.
            with pytest.raises(SystemExit):
                mesonpy.build_wheel(tmp_path)
        else:
            wheel = mesonpy.build_wheel(tmp_path)
            subprocess.run(
                [venv.executable, '-m', 'pip', 'install', tmp_path / wheel],
                check=True)
            output = subprocess.run(
                [venv.executable, '-c', 'import spam; print(spam.add(1, 2))'],
                check=True, stdout=subprocess.PIPE).stdout
            assert int(output) == 3
