import subprocess
import sys

import pytest

from mesonpy._util import chdir

from .conftest import in_git_repo_context, package_dir


@pytest.mark.usefixtures('pep518')
@pytest.mark.parametrize(
    ('package'),
    [
        'purelib-and-platlib',
    ]
)
@pytest.mark.parametrize(
    'build_arg', ['', '--wheel'], ids=['sdist_to_wheel', 'wheel_directly']
)
def test_pep518(package, build_arg, tmp_path):
    dist = tmp_path / 'dist'

    with chdir(package_dir / package), in_git_repo_context():
        build_args = [build_arg] if build_arg else []
        subprocess.run([sys.executable, '-m', 'build', '--outdir', str(dist), *build_args], check=True)
