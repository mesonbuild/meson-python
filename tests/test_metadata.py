# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import pathlib
import re

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
    match = '|'.join((
        re.escape('Required "project.version" field is missing'),
        # pyproject-metatadata 0.8.0 and later
        re.escape('Field "project.version" missing and "version" not specified in "project.dynamic"'),
        # pyproject-metatadata 0.9.0 and later
        re.escape('Field "project.version" missing and \'version\' not specified in "project.dynamic"'),
    ))
    with pytest.raises(pyproject_metadata.ConfigurationError, match=match):
        Metadata.from_pyproject(pyproject, pathlib.Path())
