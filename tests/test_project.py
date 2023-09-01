# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import ast
import os
import shutil
import sys
import textwrap


if sys.version_info < (3, 11):
    import tomli as tomllib
else:
    import tomllib

import pyproject_metadata
import pytest

import mesonpy

from .conftest import chdir, in_git_repo_context, package_dir


@pytest.mark.parametrize(
    ('package'),
    [
        'library',
        'library-pep621',
    ]
)
def test_name(package):
    with chdir(package_dir / package), mesonpy._project() as project:
        assert project.name == package.replace('-', '_')


@pytest.mark.parametrize(
    ('package'),
    [
        'library',
        'library-pep621',
    ]
)
def test_version(package):
    with chdir(package_dir / package), mesonpy._project() as project:
        assert project.version == '1.0.0'


def test_unsupported_dynamic(package_unsupported_dynamic):
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Unsupported dynamic fields: "dependencies"'):
        with mesonpy._project():
            pass


def test_unsupported_python_version(package_unsupported_python_version):
    with pytest.raises(mesonpy.MesonBuilderError, match='Package requires Python version ==1.0.0'):
        with mesonpy._project():
            pass


def test_missing_version(package_missing_version):
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Required "project.version" field is missing'):
        with mesonpy._project():
            pass


def test_missing_meson_version(package_missing_meson_version):
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Section "project" missing in pyproject.toml'):
        with mesonpy._project():
            pass


def test_missing_dynamic_version(package_missing_dynamic_version):
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Field "version" declared as dynamic but'):
        with mesonpy._project():
            pass


def test_user_args(package_user_args, tmp_path, monkeypatch):
    project_run = mesonpy.Project._run
    cmds = []
    args = []

    def wrapper(self, cmd):
        # intercept and filter out test arguments and forward the call
        if cmd[:2] == ['meson', 'compile']:
            # when using meson compile instead of ninja directly, the
            # arguments needs to be unmarshalled from the form used to
            # pass them to the --ninja-args option
            assert cmd[-1].startswith('--ninja-args=')
            cmds.append(cmd[:2])
            args.append(ast.literal_eval(cmd[-1].split('=')[1]))
        elif cmd[:1] == ['meson']:
            cmds.append(cmd[:2])
            args.append(cmd[2:])
        else:
            # direct ninja invocation
            cmds.append([os.path.basename(cmd[0])])
            args.append(cmd[1:])
        return project_run(self, [x for x in cmd if not x.startswith(('config-', 'cli-', '--ninja-args'))])

    monkeypatch.setattr(mesonpy.Project, '_run', wrapper)

    config_settings = {
        'dist-args': ('cli-dist',),
        'setup-args': ('cli-setup',),
        'compile-args': ('cli-compile',),
        'install-args': ('cli-install',),
    }

    with in_git_repo_context():
        mesonpy.build_sdist(tmp_path, config_settings)
        mesonpy.build_wheel(tmp_path, config_settings)

    # check that the right commands are executed, namely that 'meson
    # compile' is used on Windows rather than a 'ninja' direct
    # invocation.
    assert cmds == [
        # sdist: calls to 'meson setup' and 'meson dist'
        ['meson', 'setup'],
        ['meson', 'dist'],
        # wheel: calls to 'meson setup', 'meson compile', and 'meson install'
        ['meson', 'setup'],
        ['meson', 'compile'] if sys.platform == 'win32' else ['ninja'],
    ]

    # check that the user options are passed to the invoked commands
    expected = [
        # sdist: calls to 'meson setup' and 'meson dist'
        ['config-setup', 'cli-setup'],
        ['config-dist', 'cli-dist'],
        # wheel: calls to 'meson setup', 'meson compile', and 'meson install'
        ['config-setup', 'cli-setup'],
        ['config-compile', 'cli-compile'],
        ['config-install', 'cli-install'],
    ]
    for expected_args, cmd_args in zip(expected, args):
        for arg in expected_args:
            assert arg in cmd_args


@pytest.mark.parametrize('package', ('top-level', 'meson-args'))
def test_unknown_user_args(package, tmp_path_session):
    with pytest.raises(mesonpy.ConfigError):
        mesonpy.Project(package_dir / f'unknown-user-args-{package}', tmp_path_session)


def test_install_tags(package_purelib_and_platlib, tmp_path_session):
    project = mesonpy.Project(
        package_purelib_and_platlib,
        tmp_path_session,
        meson_args={
            'install': ['--tags', 'purelib'],
        }
    )
    assert project.is_pure


def test_validate_pyproject_config_one():
    pyproject_config = tomllib.loads(textwrap.dedent('''
        [tool.meson-python.args]
        setup = ['-Dfoo=true']
    '''))
    conf = mesonpy._validate_pyproject_config(pyproject_config)
    assert conf['args'] == {'setup': ['-Dfoo=true']}


def test_validate_pyproject_config_all():
    pyproject_config = tomllib.loads(textwrap.dedent('''
        [tool.meson-python.args]
        setup = ['-Dfoo=true']
        dist = []
        compile = ['-j4']
        install = ['--tags=python']
    '''))
    conf = mesonpy._validate_pyproject_config(pyproject_config)
    assert conf['args'] == {
        'setup': ['-Dfoo=true'],
        'dist': [],
        'compile': ['-j4'],
        'install': ['--tags=python']}


def test_validate_pyproject_config_unknown():
    pyproject_config = tomllib.loads(textwrap.dedent('''
        [tool.meson-python.args]
        invalid = true
    '''))
    with pytest.raises(mesonpy.ConfigError, match='Unknown configuration entry "tool.meson-python.args.invalid"'):
        mesonpy._validate_pyproject_config(pyproject_config)


def test_validate_pyproject_config_empty():
    pyproject_config = tomllib.loads(textwrap.dedent(''))
    config = mesonpy._validate_pyproject_config(pyproject_config)
    assert config == {}


@pytest.mark.skipif(
    sys.version_info < (3, 8),
    reason="unittest.mock doesn't support the required APIs for this test",
)
def test_invalid_build_dir(package_pure, tmp_path, mocker):
    meson = mocker.spy(mesonpy.Project, '_run')

    # configure the project
    project = mesonpy.Project(package_pure, tmp_path)
    assert len(meson.call_args_list) == 1
    assert meson.call_args_list[0].args[1][1] == 'setup'
    assert '--reconfigure' not in meson.call_args_list[0].args[1]
    project.build()
    meson.reset_mock()

    # subsequent builds with the same build directory result in a setup --reconfigure
    project = mesonpy.Project(package_pure, tmp_path)
    assert len(meson.call_args_list) == 1
    assert meson.call_args_list[0].args[1][1] == 'setup'
    assert '--reconfigure' in meson.call_args_list[0].args[1]
    project.build()
    meson.reset_mock()

    # corrupting the build direcory setup is run again
    tmp_path.joinpath('meson-private/coredata.dat').unlink()
    project = mesonpy.Project(package_pure, tmp_path)
    assert len(meson.call_args_list) == 1
    assert meson.call_args_list[0].args[1][1] == 'setup'
    assert '--reconfigure' not in meson.call_args_list[0].args[1]
    project.build()
    meson.reset_mock()

    # removing the build directory things should still work
    shutil.rmtree(tmp_path)
    project = mesonpy.Project(package_pure, tmp_path)
    assert len(meson.call_args_list) == 1
    assert meson.call_args_list[0].args[1][1] == 'setup'
    assert '--reconfigure' not in meson.call_args_list[0].args[1]
    project.build()


@pytest.mark.skipif(not os.getenv('CI') or sys.platform != 'win32', reason='Requires MSVC')
def test_compiler(venv, package_detect_compiler, tmp_path):
    # Check that things are setup properly to use the MSVC compiler on
    # Windows. This effectively means running the compilation step
    # with 'meson compile' instead of 'ninja' on Windows. Run this
    # test only on CI where we know that MSVC is available.
    wheel = mesonpy.build_wheel(tmp_path, {'setup-args': ['--vsenv']})
    venv.pip('install', os.fspath(tmp_path / wheel))
    compiler = venv.python('-c', 'import detect_compiler; print(detect_compiler.compiler())').strip()
    assert compiler == 'msvc'
