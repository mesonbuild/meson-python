# SPDX-License-Identifier: MIT

import contextlib
import os
import os.path
import pathlib
import shutil
import tempfile

from venv import EnvBuilder

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
        try:
            shutil.rmtree(path / '.git')
        except PermissionError:
            pass


@pytest.fixture(scope='session')
def tmp_dir_session(tmpdir_factory):
    return pathlib.Path(tempfile.mkdtemp(
        prefix='mesonpy-test-',
        dir=tmpdir_factory.mktemp('test'),
    ))


class VEnv(EnvBuilder):
    def __init__(self, env_dir):
        super().__init__(with_pip=True)
        self.create(env_dir)

    def ensure_directories(self, env_dir):
        context = super().ensure_directories(env_dir)
        # Store the path to the venv Python interpreter. There does
        # not seem to be a way to do this without subclassing.
        self.executable = context.env_exe
        return context


@pytest.fixture()
def venv():
    path = pathlib.Path(tempfile.mkdtemp(prefix='mesonpy-test-venv-'))
    venv = VEnv(path)
    try:
        yield venv
    finally:
        shutil.rmtree(path)


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
