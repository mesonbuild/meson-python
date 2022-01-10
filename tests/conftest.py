# SPDX-License-Identifier: EUPL-1.2

import contextlib
import os
import os.path
import pathlib
import shutil
import tempfile
import venv

import git
import pytest

import mesonpy


package_dir = pathlib.Path(__file__).parent / 'packages'


@contextlib.contextmanager
def cd_package(package):
    cur_dir = os.getcwd()
    package_path = package_dir / package
    os.chdir(package_path)
    try:
        yield package_path
    finally:
        os.chdir(cur_dir)


@contextlib.contextmanager
def in_git_repo_context(path=os.path.curdir):
    path = pathlib.Path(path)
    assert path.absolute().relative_to(package_dir)
    shutil.rmtree(path / '.git', ignore_errors=True)
    try:
        handler = git.Git(path)
        handler.init()
        handler.config('commit.gpgsign', 'false')
        handler.config('user.name', 'Example')
        handler.config('user.email', 'example@example.com')
        handler.add('*')
        handler.commit('--allow-empty-message', '-m', '')
        handler.tag('-a', '-m', '', '1.0.0')
        yield
    finally:
        shutil.rmtree(path / '.git')


@pytest.fixture(scope='session')
def tmp_dir_session():
    path = tempfile.mkdtemp(prefix='mesonpy-test-')

    try:
        yield pathlib.Path(path)
    finally:
        try:
            shutil.rmtree(path)
        except PermissionError:  # pragma: no cover
            pass  # this sometimes fails on windows :/


@pytest.fixture()
def virtual_env():
    path = pathlib.Path(tempfile.mkdtemp(prefix='mesonpy-test-venv-'))

    venv.create(path, with_pip=True)
    try:
        # FIXME: windows
        yield path / 'bin' / 'python'
    finally:
        try:
            shutil.rmtree(path)
        except PermissionError:  # pragma: no cover
            pass  # this sometimes fails on windows :/


def generate_package_fixture(package):
    @pytest.fixture
    def fixture():
        with cd_package(package) as new_path:
            yield new_path
    return fixture


def generate_sdist_fixture(package):
    @pytest.fixture(scope='session')
    def fixture(tmp_dir_session):
        with cd_package(package), in_git_repo_context():
            return tmp_dir_session / mesonpy.build_sdist(tmp_dir_session)
    return fixture


def generate_wheel_fixture(package):
    @pytest.fixture(scope='session')
    def fixture(tmp_dir_session):
        with cd_package(package), in_git_repo_context():
            return tmp_dir_session / mesonpy.build_wheel(tmp_dir_session)
    return fixture


# inject {package,sdist,wheel}_* fixtures (https://github.com/pytest-dev/pytest/issues/2424)
for package in os.listdir(package_dir):
    normalized = package.replace('-', '_')
    globals()[f'package_{normalized}'] = generate_package_fixture(package)
    globals()[f'sdist_{normalized}'] = generate_sdist_fixture(package)
    globals()[f'wheel_{normalized}'] = generate_wheel_fixture(package)
