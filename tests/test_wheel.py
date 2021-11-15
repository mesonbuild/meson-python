# SPDX-License-Identifier: EUPL-1.2

import re
import sysconfig

import wheel.wheelfile


EXT_SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')


def wheel_contents(artifact):
    # Sometimes directories have entries, sometimes not, so we filter them out.
    return {
        entry for entry in artifact.namelist()
        if not entry.endswith('/')
    }


def test_contents(package_library, wheel_library):
    artifact = wheel.wheelfile.WheelFile(wheel_library)

    for name, regex in zip(sorted(wheel_contents(artifact)), [
        re.escape('library-1.0.0.data/scripts/example'),
        re.escape('library-1.0.0.dist-info/METADATA'),
        re.escape('library-1.0.0.dist-info/RECORD'),
        re.escape('library-1.0.0.dist-info/WHEEL'),
        r'library\.libs/libexample.*\.so',
    ]):
        assert re.match(regex, name), f'`{name}` does not match `{regex}`'


def test_purelib_and_platlib(wheel_purelib_and_platlib):
    artifact = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib)

    assert wheel_contents(artifact) == {
        f'plat{EXT_SUFFIX}',
        'purelib_and_platlib-1.0.0.data/purelib/pure.py',
        'purelib_and_platlib-1.0.0.dist-info/METADATA',
        'purelib_and_platlib-1.0.0.dist-info/RECORD',
        'purelib_and_platlib-1.0.0.dist-info/WHEEL',
    }


def test_pure(wheel_pure):
    artifact = wheel.wheelfile.WheelFile(wheel_pure)

    assert wheel_contents(artifact) == {
        'pure-1.0.0.dist-info/METADATA',
        'pure-1.0.0.dist-info/RECORD',
        'pure-1.0.0.dist-info/WHEEL',
        'pure.py',
    }


def test_configure_data(wheel_configure_data):
    artifact = wheel.wheelfile.WheelFile(wheel_configure_data)

    assert wheel_contents(artifact) == {
        'configure_data-1.0.0.data/platlib/configure_data.py',
        'configure_data-1.0.0.dist-info/METADATA',
        'configure_data-1.0.0.dist-info/RECORD',
        'configure_data-1.0.0.dist-info/WHEEL',
    }
