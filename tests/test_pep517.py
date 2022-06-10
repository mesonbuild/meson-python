# SPDX-License-Identifier: MIT

import platform

import pytest

import mesonpy

from .conftest import cd_package


if platform.system() == 'Linux':
    VENDORING_DEPS = {mesonpy._depstr.patchelf}
else:
    VENDORING_DEPS = set()


@pytest.mark.parametrize(
    ('package', 'system_patchelf', 'expected'),
    [
        ('pure', True, set()),  # pure and system patchelf
        ('library', True, set()),  # not pure and system patchelf
        ('pure', False, set()),  # pure and no system patchelf
        ('library', False, VENDORING_DEPS),  # not pure and no system patchelf
    ]
)
def test_get_requires_for_build_wheel(mocker, package, expected, system_patchelf):
    mock = mocker.patch('shutil.which', return_value=system_patchelf)

    if mock.called:  # sanity check for the future if we add another usage
        mock.assert_called_once_with('patchelf')

    with cd_package(package):
        assert set(mesonpy.get_requires_for_build_wheel()) == expected | {
            mesonpy._depstr.wheel,
        }
