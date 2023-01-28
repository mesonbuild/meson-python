# SPDX-FileCopyrightText: 2023 meson-python developers
#
# SPDX-License-Identifier: MIT

import contextlib
import os
import os.path
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import warnings

from venv import EnvBuilder

import pytest

import mesonpy

from mesonpy._util import chdir


def adjust_packaging_platform_tag(platform: str) -> str:
    if platform.startswith(('manylinux', 'musllinux')):
        # The packaging module generates overly specific platforms tags on
        # Linux.  The platforms tags on Linux evolved over time.
        # meson-python uses more relaxed platform tags to maintain
        # compatibility with old wheel installation tools.  The relaxed
        # platform tags match the ones generated by the wheel package.
        # https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/
        return re.sub(r'^(many|musl)linux(1|2010|2014|_\d+_\d+)_(.*)$', r'linux_\3', platform)
    if platform.startswith('macosx'):
        # Python built with older macOS SDK on macOS 11, reports an
        # unexising macOS 10.16 version instead of the real version.
        # The packaging module introduced a workaround in version
        # 22.0.  Too maintain compatibility with older packaging
        # releases we don't implement it.  Reconcile this.
        from platform import mac_ver
        version = tuple(map(int, mac_ver()[0].split('.')))[:2]
        if version == (10, 16):
            return re.sub(r'^macosx_\d+_\d+_(.*)$', r'macosx_10_16_\1', platform)
    return platform


package_dir = pathlib.Path(__file__).parent / 'packages'


@contextlib.contextmanager
def in_git_repo_context(path=os.path.curdir):
    # Resist the tentation of using pathlib.Path here: it is not
    # supporded by subprocess in Python 3.7.
    path = os.path.abspath(path)
    shutil.rmtree(os.path.join(path, '.git'), ignore_errors=True)
    try:
        subprocess.run(['git', 'init', '-b', 'main', path], check=True)
        subprocess.run(['git', 'config', 'user.email', 'author@example.com'], cwd=path, check=True)
        subprocess.run(['git', 'config', 'user.name', 'A U Thor'], cwd=path, check=True)
        subprocess.run(['git', 'add', '*'], cwd=path, check=True)
        subprocess.run(['git', 'commit', '-q', '-m', 'Test'], cwd=path, check=True)
        yield
    finally:
        # PermissionError raised on Windows.
        with contextlib.suppress(PermissionError):
            shutil.rmtree(os.path.join(path, '.git'))


@pytest.fixture(scope='session')
def tmp_path_session(tmp_path_factory):
    return pathlib.Path(tempfile.mkdtemp(
        prefix='mesonpy-test-',
        dir=tmp_path_factory.mktemp('test'),
    ))


class VEnv(EnvBuilder):
    def __init__(self, env_dir):
        super().__init__(with_pip=True)
        # This warning is mistakenly generated by CPython 3.11.0
        # https://github.com/python/cpython/pull/98743
        with warnings.catch_warnings():
            if sys.version_info[:3] == (3, 11, 0):
                warnings.filterwarnings('ignore', 'check_home argument is deprecated and ignored.', DeprecationWarning)
            self.create(env_dir)

    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        # Store the path to the venv Python interpreter. There does
        # not seem to be a way to do this without subclassing.
        self.executable = context.env_exe
        return context

    def python(self, *args: str):
        return subprocess.check_output([self.executable, *args]).decode()

    def pip(self, *args: str):
        return self.python('-m', 'pip', *args)


@pytest.fixture()
def venv(tmp_path_factory):
    path = pathlib.Path(tmp_path_factory.mktemp('mesonpy-test-venv'))
    return VEnv(path)


def generate_package_fixture(package):
    @pytest.fixture
    def fixture():
        with chdir(package_dir / package) as new_path:
            yield new_path
    return fixture


def generate_sdist_fixture(package):
    @pytest.fixture(scope='session')
    def fixture(tmp_path_session):
        with chdir(package_dir / package), in_git_repo_context():
            return tmp_path_session / mesonpy.build_sdist(tmp_path_session)
    return fixture


def generate_wheel_fixture(package):
    @pytest.fixture(scope='session')
    def fixture(tmp_path_session):
        with chdir(package_dir / package), in_git_repo_context():
            return tmp_path_session / mesonpy.build_wheel(tmp_path_session)
    return fixture


def generate_editable_fixture(package):
    @pytest.fixture(scope='session')
    def fixture(tmp_path_session):
        with chdir(package_dir / package), in_git_repo_context():
            return tmp_path_session / mesonpy.build_editable(tmp_path_session)
    return fixture


# inject {package,sdist,wheel}_* fixtures (https://github.com/pytest-dev/pytest/issues/2424)
for package in os.listdir(package_dir):
    normalized = package.replace('-', '_')
    globals()[f'package_{normalized}'] = generate_package_fixture(package)
    globals()[f'sdist_{normalized}'] = generate_sdist_fixture(package)
    globals()[f'wheel_{normalized}'] = generate_wheel_fixture(package)
    globals()[f'editable_{normalized}'] = generate_editable_fixture(package)


@pytest.fixture(autouse=True, scope='session')
def disable_pip_version_check():
    # Cannot use the 'monkeypatch' fixture because of scope mismatch.
    mpatch = pytest.MonkeyPatch()
    yield mpatch.setenv('PIP_DISABLE_PIP_VERSION_CHECK', '1')
    mpatch.undo()


@pytest.fixture(scope='session')
def pep518_wheelhouse(tmp_path_factory):
    wheelhouse = tmp_path_factory.mktemp('wheelhouse')
    meson_python = str(package_dir.parent.parent)
    # Populate wheelhouse with wheel for the following packages and
    # their dependencies.  Wheels are downloaded from PyPI or built
    # from the source distribution as needed.  Sources or wheels in
    # the pip cache are used when available.
    packages = [
        meson_python,
    ]
    subprocess.run([sys.executable, '-m', 'pip', 'wheel', '--wheel-dir', str(wheelhouse), *packages], check=True)
    return str(wheelhouse)


@pytest.fixture
def pep518(pep518_wheelhouse, monkeypatch):
    monkeypatch.setenv('PIP_FIND_LINKS', pep518_wheelhouse)
    monkeypatch.setenv('PIP_NO_INDEX', 'true')
