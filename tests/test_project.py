# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import platform

import pyproject_metadata
import pytest

import mesonpy

from mesonpy._config import BuildHookSettings

from .conftest import chdir, package_dir


@pytest.mark.parametrize(
    ('package'),
    [
        'library',
        'library-pep621',
    ]
)
def test_name(package):
    with chdir(package_dir / package), mesonpy.Project.with_temp_working_dir() as project:
        assert project.name == package.replace('-', '_')


@pytest.mark.parametrize(
    ('package'),
    [
        'library',
        'library-pep621',
    ]
)
def test_version(package):
    with chdir(package_dir / package), mesonpy.Project.with_temp_working_dir() as project:
        assert project.version == '1.0.0'


def test_unsupported_dynamic(package_unsupported_dynamic):
    with pytest.raises(mesonpy.MesonBuilderError, match='Unsupported dynamic fields: "dependencies"'):
        with mesonpy.Project.with_temp_working_dir():
            pass


def test_unsupported_python_version(package_unsupported_python_version):
    with pytest.raises(mesonpy.MesonBuilderError, match=(
        f'Unsupported Python version {platform.python_version()}, expected ==1.0.0'
    )):
        with mesonpy.Project.with_temp_working_dir():
            pass


def test_user_args(package_user_args, tmp_path, monkeypatch):
    project_run = mesonpy.Project._run
    call_args_list = []

    def wrapper(self, cmd):
        # intercept and filter out test arguments and forward the call
        call_args_list.append(tuple(cmd))
        return project_run(self, [x for x in cmd if not x.startswith(('config-', 'cli-'))])

    monkeypatch.setattr(mesonpy.Project, '_run', wrapper)

    def last_two_meson_args():
        return [args[-2:] for args in call_args_list]

    config_settings = {
        'dist-args': ('cli-dist',),
        'setup-args': ('cli-setup',),
        'compile-args': ('cli-compile',),
        'install-args': ('cli-install',),
    }

    mesonpy.build_sdist(tmp_path, config_settings)
    mesonpy.build_wheel(tmp_path, config_settings)

    assert last_two_meson_args() == [
        # sdist: calls to 'meson setup' and 'meson dist'
        ('config-setup', 'cli-setup'),
        ('config-dist', 'cli-dist'),
        # wheel: calls to 'meson setup', 'meson compile', and 'meson install'
        ('config-setup', 'cli-setup'),
        ('config-compile', 'cli-compile'),
        ('config-install', 'cli-install'),
    ]


@pytest.mark.parametrize('package', ('top-level', 'meson-args'))
def test_unknown_user_args(package, tmp_path_session):
    with pytest.raises(pyproject_metadata.ConfigurationError):
        mesonpy.Project(package_dir / f'unknown-user-args-{package}', tmp_path_session)


def test_install_tags(package_purelib_and_platlib, tmp_path_session):
    project = mesonpy.Project(
        package_purelib_and_platlib,
        tmp_path_session,
        hook_settings=BuildHookSettings.from_config_settings({
            'install-args': ['--tags', 'purelib'],
        }),
    )
    assert project.is_pure
