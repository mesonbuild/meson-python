# SPDX-License-Identifier: EUPL-1.2

import pytest

import mesonpy


def test_unsupported_dynamic(package_unsupported_dynamic):
    with pytest.raises(mesonpy.MesonBuilderError, match='Unsupported dynamic fields: dependencies'):
        with mesonpy.Project.with_temp_working_dir():
            pass
