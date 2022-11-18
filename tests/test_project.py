# SPDX-License-Identifier: MIT

import contextlib
import platform
import subprocess
import sys

import pytest

import mesonpy

from .conftest import cd_package, package_dir


@pytest.mark.parametrize(
    ('package'),
    [
        'library',
        'library-pep621',
    ]
)
def test_name(package):
    with cd_package(package), mesonpy.Project.with_temp_working_dir() as project:
        assert project.name == package.replace('-', '_')


@pytest.mark.parametrize(
    ('package'),
    [
        'library',
        'library-pep621',
    ]
)
def test_version(package):
    with cd_package(package), mesonpy.Project.with_temp_working_dir() as project:
        assert project.version == '1.0.0'


def test_unsupported_dynamic(package_unsupported_dynamic):
    with pytest.raises(mesonpy.MesonBuilderError, match='Unsupported dynamic fields: dependencies'):
        with mesonpy.Project.with_temp_working_dir():
            pass


def test_unsupported_python_version(package_unsupported_python_version):
    with pytest.raises(mesonpy.MesonBuilderError, match=(
        f'Unsupported Python version `{platform.python_version()}`, '
        'expected `==1.0.0`'
    )):
        with mesonpy.Project.with_temp_working_dir():
            pass


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="unittest.mock doesn't support the required APIs for this test",
)
def test_user_args(package_user_args, mocker, tmp_dir_session):
    mocker.patch('mesonpy.Project._meson')

    def last_two_meson_args():
        return [
            call.args[-2:] for call in mesonpy.Project._meson.call_args_list
        ]

    # create the build directory ourselves because Project._meson is mocked
    builddir = str(tmp_dir_session / 'build')
    subprocess.run(['meson', 'setup', '.', builddir], check=True)

    config_settings = {
        'builddir': builddir,  # use the build directory we created
        'dist-args': ('cli-dist',),
        'setup-args': ('cli-setup',),
        'compile-args': ('cli-compile',),
        'install-args': ('cli-install',),
    }

    with contextlib.suppress(Exception):
        mesonpy.build_sdist(tmp_dir_session / 'dist', config_settings)
    with contextlib.suppress(Exception):
        mesonpy.build_wheel(tmp_dir_session / 'dist', config_settings)

    assert last_two_meson_args() == [
        # sdist
        ('config-setup', 'cli-setup'),
        ('config-dist', 'cli-dist'),
        # wheel
        ('config-setup', 'cli-setup'),
        ('config-compile', 'cli-compile'),
        ('config-install', 'cli-install'),
    ]


@pytest.mark.parametrize('package', ('top-level', 'meson-args'))
def test_unknown_user_args(package, tmp_dir_session):
    with pytest.raises(mesonpy.ConfigError):
        mesonpy.Project(package_dir / f'unknown-user-args-{package}', tmp_dir_session)
