# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import pathlib
import sys


if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def test_pyproject_dependencies():
    pyproject = pathlib.Path(__file__).parent.parent.joinpath('pyproject.toml')
    with open(pyproject, 'rb') as f:
        data = tomllib.load(f)
    build_dependencies = data['build-system']['requires']
    project_dependencies = data['project']['dependencies']
    # verify that all build dependencies are project dependencies
    assert not set(build_dependencies) - set(project_dependencies), \
        'pyproject.toml is inconsistent: not all "build-system.requires" are in "project.dependencies"'
