# SPDX-License-Identifier: EUPL-1.2

import pytest

import mesonpy

from .conftest import cd_package


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
