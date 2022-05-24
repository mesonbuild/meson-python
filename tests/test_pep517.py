# SPDX-License-Identifier: EUPL-1.2

import platform

import pytest

import mesonpy

from .conftest import cd_package


if platform.system() == 'Linux':
    VENDORING_DEPS = {mesonpy._depstr.patchelf_wrapper}
else:
    VENDORING_DEPS = set()


@pytest.mark.parametrize(
    ('package', 'expected'),
    [
        ('pure', set()),  # pure and no PEP 621
        ('library', VENDORING_DEPS),  # not pure and not PEP 621
    ]
)
def test_get_requires_for_build_wheel(package, expected):
    with cd_package(package):
        assert set(mesonpy.get_requires_for_build_wheel()) == expected | {
            mesonpy._depstr.wheel,
            mesonpy._depstr.ninja,
        }
