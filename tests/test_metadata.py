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


def test_unsupported_dynamic():
    pyproject = {'project': {
        'name': 'unsupported-dynamic',
        'version': '0.0.1',
        'dynamic': ['dependencies'],
    }}
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Unsupported dynamic fields: "dependencies"'):
        Metadata.from_pyproject(pyproject, pathlib.Path())


def test_missing_version(package_missing_version):
    pyproject = {'project': {
        'name': 'missing-version',
    }}
    with pytest.raises(pyproject_metadata.ConfigurationError, match='Required "project.version" field is missing'):
        Metadata.from_pyproject(pyproject, pathlib.Path())
