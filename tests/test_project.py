# SPDX-License-Identifier: MIT

import contextlib
import platform
import subprocess
import sys

import pytest

import mesonpy

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


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="unittest.mock doesn't support the required APIs for this test",
)
def test_user_args(package_user_args, mocker, tmp_path_session):
    mocker.patch('mesonpy.Project._meson')

    def last_two_meson_args():
        return [call.args[-2:] for call in mesonpy.Project._meson.call_args_list]

    # create the build directory ourselves because Project._meson is mocked
    builddir = str(tmp_path_session / 'build')

    config_settings = {
        'builddir': builddir,  # use the build directory we created
        'dist-args': ('cli-dist',),
        'setup-args': ('cli-setup',),
        'compile-args': ('cli-compile',),
        'install-args': ('cli-install',),
    }

    with contextlib.suppress(FileNotFoundError):
        mesonpy.build_sdist(tmp_path_session / 'dist', config_settings)

    # run setup ourselves because Project._meson is mocked
    subprocess.run(['meson', 'setup', '.', builddir], check=True)

    with contextlib.suppress(FileNotFoundError):
        mesonpy.build_wheel(tmp_path_session / 'dist', config_settings)

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
    with pytest.raises(mesonpy.ConfigError):
        mesonpy.Project(package_dir / f'unknown-user-args-{package}', tmp_path_session)
