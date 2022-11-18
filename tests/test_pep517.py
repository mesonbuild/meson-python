# SPDX-License-Identifier: MIT

import shutil
import subprocess
import sys

from typing import List

import pytest

import mesonpy

from .conftest import cd_package


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

    def run(cmd: List[str], *args: object, **kwargs: object) -> subprocess.CompletedProcess:
        if cmd != ['ninja', '--version']:
            # smoke check for the future if we add another usage
            raise AssertionError(f'Called with {cmd}, tests not expecting that usage')
        return subprocess.CompletedProcess(cmd, 0, f'{ninja}\n', '')

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

    with cd_package(package):
        assert set(mesonpy.get_requires_for_build_wheel()) == expected


def test_invalid_config_settings(package_pure, tmp_dir_session):
    raises_error = pytest.raises(mesonpy.ConfigError, match='Unknown config setting: invalid')

    with raises_error:
        mesonpy.build_sdist(tmp_dir_session, {'invalid': ()})
    with raises_error:
        mesonpy.build_wheel(tmp_dir_session, {'invalid': ()})
