# SPDX-License-Identifier: EUPL-1.2

import re

import wheel.wheelfile


def test_contents(package_library, wheel_library):
    artifact = wheel.wheelfile.WheelFile(wheel_library)

    for name, regex in zip(artifact.namelist(), [
        r'library\.libs/libexample.*\.so',
    ] + list(map(re.escape, [
        'library-1.0.0.data/scripts/example',
        'library-1.0.0.dist-info/RECORD',
        'library-1.0.0.dist-info/WHEEL',
        'library-1.0.0.dist-info/METADATA',
    ]))):
        assert re.match(regex, name), f'`{name}` does not match `{regex}`'


def test_purelib_and_platlib(wheel_purelib_and_platlib):
    artifact = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib)

    assert artifact.namelist() == [
        'purelib_and_platlib-1.0.0.dist-info/METADATA',
        'purelib_and_platlib-1.0.0.dist-info/WHEEL',
        'pure.py',
        'purelib_and_platlib-1.0.0.data/platlib/plat.cpython-39-x86_64-linux-gnu.so',
        'purelib_and_platlib-1.0.0.dist-info/RECORD',
    ]


def test_pure(wheel_pure):
    artifact = wheel.wheelfile.WheelFile(wheel_pure)

    assert artifact.namelist() == [
        'pure-1.0.0.dist-info/METADATA',
        'pure-1.0.0.dist-info/WHEEL',
        'pure.py',
        'pure-1.0.0.dist-info/RECORD',
    ]
