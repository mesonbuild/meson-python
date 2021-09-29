# SPDX-License-Identifier: EUPL-1.2

import re
import sysconfig

import wheel.wheelfile


EXT_SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')


def test_contents(package_library, wheel_library):
    artifact = wheel.wheelfile.WheelFile(wheel_library)

    for name, regex in zip(sorted(artifact.namelist()), [
        re.escape('library-1.0.0.data/'),
        re.escape('library-1.0.0.data/scripts'),
        re.escape('library-1.0.0.data/scripts/example'),
        re.escape('library-1.0.0.dist-info/'),
        re.escape('library-1.0.0.dist-info/METADATA'),
        re.escape('library-1.0.0.dist-info/RECORD'),
        re.escape('library-1.0.0.dist-info/WHEEL'),
        re.escape('library.libs/'),
        r'library\.libs/libexample.*\.so',
    ]):
        assert re.match(regex, name), f'`{name}` does not match `{regex}`'


def test_purelib_and_platlib(wheel_purelib_and_platlib):
    artifact = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib)

    assert set(artifact.namelist()) == {
        f'plat{EXT_SUFFIX}',
        'purelib_and_platlib-1.0.0.data/',
        'purelib_and_platlib-1.0.0.data/purelib/',
        'purelib_and_platlib-1.0.0.data/purelib/pure.py',
        'purelib_and_platlib-1.0.0.dist-info/',
        'purelib_and_platlib-1.0.0.dist-info/METADATA',
        'purelib_and_platlib-1.0.0.dist-info/RECORD',
        'purelib_and_platlib-1.0.0.dist-info/WHEEL',
        'purelib_and_platlib.libs/',
    }


def test_pure(wheel_pure):
    artifact = wheel.wheelfile.WheelFile(wheel_pure)

    assert set(artifact.namelist()) == {
        'pure-1.0.0.dist-info/METADATA',
        'pure-1.0.0.dist-info/RECORD',
        'pure-1.0.0.dist-info/WHEEL',
        'pure.py',
    }


def test_configure_data(wheel_configure_data):
    artifact = wheel.wheelfile.WheelFile(wheel_configure_data)

    assert set(artifact.namelist()) == {
        'configure_data-1.0.0.data/platlib/configure_data.py',
        'configure_data-1.0.0.dist-info/METADATA',
        'configure_data-1.0.0.dist-info/RECORD',
        'configure_data-1.0.0.dist-info/WHEEL',
    }
