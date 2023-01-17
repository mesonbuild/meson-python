# SPDX-License-Identifier: MIT

import shutil
import subprocess
import sys

from typing import List

import pytest

import mesonpy

from mesonpy._util import chdir

from .conftest import package_dir


@pytest.mark.parametrize('package', ['pure', 'library'])
@pytest.mark.parametrize('system_patchelf', ['patchelf', None], ids=['patchelf', 'nopatchelf'])
@pytest.mark.parametrize('ninja', [None, '1.8.1', '1.8.3'], ids=['noninja', 'oldninja', 'newninja'])
def test_get_requires_for_build_wheel(monkeypatch, package, system_patchelf, ninja):
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

    ninja_available = ninja is not None and [int(x) for x in ninja.split('.')] >= [1, 8, 2]

    if not ninja_available:
        expected |= {mesonpy._depstr.ninja}

    if (
        system_patchelf is None and sys.platform.startswith('linux')
        and (not ninja_available or (ninja_available and package != 'pure'))
    ):
        expected |= {mesonpy._depstr.patchelf}

    with chdir(package_dir / package):
        assert set(mesonpy.get_requires_for_build_wheel()) == expected


def test_invalid_config_settings(capsys, package_pure, tmp_path_session):
    for method in mesonpy.build_sdist, mesonpy.build_wheel:
        with pytest.raises(SystemExit):
            method(tmp_path_session, {'invalid': ()})
        out, err = capsys.readouterr()
        assert out.splitlines()[-1].endswith(
            'Unknown configuration entry "invalid"')


def test_invalid_config_settings_suggest(capsys, package_pure, tmp_path_session):
    for method in mesonpy.build_sdist, mesonpy.build_wheel:
        with pytest.raises(SystemExit):
            method(tmp_path_session, {'setup_args': ()})
        out, err = capsys.readouterr()
        assert out.splitlines()[-1].endswith(
            'Unknown configuration entry "setup_args". Did you mean "setup-args" or "dist-args"?')
