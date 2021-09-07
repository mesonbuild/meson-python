# SPDX-License-Identifier: EUPL-1.2

import pytest

import mesonpy

from .conftest import cd_package


@pytest.mark.parametrize(
    ('package', 'expected'),
    [
        ('pure', set()),  # no PEP 621
        ('full-metadata', {'pep621 >= 0.2.0'}),  # PEP 621
    ]
)
def test_get_requires_for_build_sdist(package, expected):
    with cd_package(package):
        assert set(mesonpy.get_requires_for_build_sdist()) == expected


@pytest.mark.parametrize(
    ('package', 'expected'),
    [
        ('pure', set()),  # pure and no PEP 621
        ('full-metadata', {'pep621 >= 0.2.0'}),  # pure and PEP 621
        ('library', {'auditwheel >= 4.0.0'}),  # not pure and not PEP 621
        ('library-pep621', {'auditwheel >= 4.0.0', 'pep621 >= 0.2.0'}),  # not pure and PEP 621
    ]
)
def test_get_requires_for_build_wheel(package, expected):
    with cd_package(package):
        assert set(mesonpy.get_requires_for_build_wheel()) == expected | {'wheel >= 0.36.0', 'ninja'}
