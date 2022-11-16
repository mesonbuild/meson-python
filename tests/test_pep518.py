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
@pytest.mark.xfail(sys.platform.startswith('cygwin'), reason='ninja pip package not available on cygwin', strict=True)
def test_pep518(pep518, package, build_arg, tmp_path):
    dist = tmp_path / 'dist'

    with cd_package(package) as package_dir, in_git_repo_context():
        build_args = [build_arg] if build_arg else []
        subprocess.run([sys.executable, '-m', 'build', f'--outdir={dist}', *build_args], cwd=package_dir, check=True)
