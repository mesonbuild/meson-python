import subprocess
import sys

import pytest

from .conftest import cd_package, in_git_repo_context


@pytest.mark.parametrize(
    ('package'),
    [
        'purelib-and-platlib',
    ]
)
@pytest.mark.parametrize(
    'build_arg', ['', '--wheel'], ids=['sdist_to_wheel', 'wheel_directly']
)
def test_pep518(pep518, package, build_arg, tmp_path):
    dist = tmp_path / 'dist'

    with cd_package(package), in_git_repo_context():
        build_args = [build_arg] if build_arg else []
        subprocess.run([sys.executable, '-m', 'build', '--outdir', str(dist), *build_args], check=True)
