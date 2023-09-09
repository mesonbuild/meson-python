# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import pathlib

import packaging.version
import pyproject_metadata
import pytest

from mesonpy import Metadata


def test_package_name():
    name = 'package.Test'
    metadata = Metadata(name='package.Test', version=packaging.version.Version('0.0.1'))
    assert metadata.name == name
    assert metadata.canonical_name == 'package-test'


def test_package_name_from_pyproject():
    name = 'package.Test'
    pyproject = {'project': {
        'name': 'package.Test',
        'version': '0.0.1',
    }}
    metadata = Metadata.from_pyproject(pyproject, pathlib.Path())
    assert metadata.name == name
    assert metadata.canonical_name == 'package-test'


def test_package_name_invalid():
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Invalid project name'):
        Metadata(name='.test', version=packaging.version.Version('0.0.1'))
