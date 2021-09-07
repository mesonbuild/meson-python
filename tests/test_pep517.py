# SPDX-License-Identifier: EUPL-1.2

import mesonpy


def test_get_requires_for_build_sdist_no_pep621(package_pure):
    assert mesonpy.get_requires_for_build_sdist() == []


def test_get_requires_for_build_sdist_pep621(package_full_metadata):
    assert mesonpy.get_requires_for_build_sdist() == ['pep621 >= 0.2.0']
