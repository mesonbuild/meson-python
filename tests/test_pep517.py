# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import re
import shutil
import subprocess
import sys
import textwrap

from typing import List

import packaging.requirements
import pytest

import mesonpy


@pytest.mark.parametrize('system_patchelf', ['patchelf', None], ids=['patchelf', 'nopatchelf'])
@pytest.mark.parametrize('ninja', [None, '1.8.1', '1.8.3'], ids=['noninja', 'oldninja', 'newninja'])
def test_get_requires_for_build_wheel(monkeypatch, package_pure, system_patchelf, ninja):
    # the NINJA environment variable affects the ninja executable lookup and breaks the test
    monkeypatch.delenv('NINJA', raising=False)

    def which(prog: str) -> bool:
        if prog == 'patchelf':
            return system_patchelf
        if prog == 'ninja':
            return ninja and 'ninja'
        if prog in ('ninja-build', 'samu'):
            return None
        # smoke check for the future if we add another usage
        raise AssertionError(f'Called with {prog}, tests not expecting that usage')

    subprocess_run = subprocess.run

    def run(cmd: List[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess:
        if cmd == ['ninja', '--version']:
            return subprocess.CompletedProcess(cmd, 0, f'{ninja}\n', '')
        return subprocess_run(cmd, *args, **kwargs)

    monkeypatch.setattr(shutil, 'which', which)
    monkeypatch.setattr(subprocess, 'run', run)

    expected = set()

    if ninja is None or mesonpy._parse_version_string(ninja) < (1, 8, 2):
        expected.add('ninja')

    if system_patchelf is None and sys.platform.startswith('linux'):
        expected.add('patchelf')

    requirements = mesonpy.get_requires_for_build_wheel()

    # Check that the requirement strings are in the correct format.
    names = {packaging.requirements.Requirement(x).name for x in requirements}

    assert names == expected


def test_invalid_config_settings(capsys, package_pure, tmp_path_session):
    for method in mesonpy.build_sdist, mesonpy.build_wheel:
        with pytest.raises(SystemExit):
            method(tmp_path_session, {'invalid': ()})
        out, err = capsys.readouterr()
        assert 'Unknown option "invalid"' in out


def test_invalid_config_settings_suggest(capsys, package_pure, tmp_path_session):
    for method in mesonpy.build_sdist, mesonpy.build_wheel:
        with pytest.raises(SystemExit):
            method(tmp_path_session, {'setup_args': ()})
        out, err = capsys.readouterr()
        assert 'Unknown option "setup_args". Did you mean "setup-args" or "dist-args"?' in out


def test_validate_config_settings_invalid():
    with pytest.raises(mesonpy.ConfigError, match='Unknown option "invalid"'):
        mesonpy._validate_config_settings({'invalid': ()})


def test_validate_config_settings_repeated():
    with pytest.raises(mesonpy.ConfigError, match='Only one value for "builddir" can be specified'):
        mesonpy._validate_config_settings({'builddir': ['one', 'two']})


def test_validate_config_settings_str():
    config = mesonpy._validate_config_settings({'setup-args': '-Dfoo=true'})
    assert config['setup-args'] == ['-Dfoo=true']


def test_validate_config_settings_list():
    config = mesonpy._validate_config_settings({'setup-args': ['-Done=1', '-Dtwo=2']})
    assert config['setup-args'] == ['-Done=1', '-Dtwo=2']


def test_validate_config_settings_tuple():
    config = mesonpy._validate_config_settings({'setup-args': ('-Done=1', '-Dtwo=2')})
    assert config['setup-args'] == ['-Done=1', '-Dtwo=2']


@pytest.mark.parametrize('meson', [None, 'meson'])
def test_get_meson_command(monkeypatch, meson):
    # The MESON environment variable affects the meson executable lookup and breaks the test.
    monkeypatch.delenv('MESON', raising=False)
    assert mesonpy._get_meson_command(meson) == ['meson']


def test_get_meson_command_bad_path(monkeypatch):
    # The MESON environment variable affects the meson executable lookup and breaks the test.
    monkeypatch.delenv('MESON', raising=False)
    with pytest.raises(mesonpy.ConfigError, match=re.escape('meson executable "bad" not found')):
        mesonpy._get_meson_command('bad')


def test_get_meson_command_bad_python_path(monkeypatch):
    # The MESON environment variable affects the meson executable lookup and breaks the test.
    monkeypatch.delenv('MESON', raising=False)
    with pytest.raises(mesonpy.ConfigError, match=re.escape('Could not find the specified meson: "bad-python-path.py"')):
        mesonpy._get_meson_command('bad-python-path.py')


def test_get_meson_command_wrong_version(monkeypatch, tmp_path):
    # The MESON environment variable affects the meson executable lookup and breaks the test.
    monkeypatch.delenv('MESON', raising=False)
    meson = tmp_path / 'meson.py'
    meson.write_text(textwrap.dedent('''
        print('0.0.1')
    '''))
    with pytest.raises(mesonpy.ConfigError, match=r'Could not find meson version [0-9\.]+ or newer, found 0\.0\.1\.'):
        mesonpy._get_meson_command(os.fspath(meson))


def test_get_meson_command_error(monkeypatch, tmp_path):
    # The MESON environment variable affects the meson executable lookup and breaks the test.
    monkeypatch.delenv('MESON', raising=False)
    meson = tmp_path / 'meson.py'
    meson.write_text(textwrap.dedent('''
        import sys
        print('Just testing', file=sys.stderr)
        sys.exit(1)
    '''))
    with pytest.raises(mesonpy.ConfigError, match=re.escape('Could not execute meson: Just testing')):
        mesonpy._get_meson_command(os.fspath(meson))
