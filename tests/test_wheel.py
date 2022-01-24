# SPDX-License-Identifier: EUPL-1.2

import platform
import re
import subprocess
import sys
import sysconfig

import wheel.wheelfile


EXT_SUFFIX = sysconfig.get_config_var('EXT_SUFFIX')
INTERPRETER_VERSION = f'{sys.version_info[0]}{sys.version_info[1]}'


if platform.python_implementation() == 'CPython':
    INTERPRETER_TAG = f'cp{INTERPRETER_VERSION}'
    PYTHON_TAG = INTERPRETER_TAG
    # Py_UNICODE_SIZE has been a runtime option since Python 3.3,
    # so the u suffix no longer exists
    if sysconfig.get_config_var('Py_DEBUG'):
        INTERPRETER_TAG += 'd'
    # https://github.com/pypa/packaging/blob/5984e3b25f4fdee64aad20e98668c402f7ed5041/packaging/tags.py#L147-L150
    if sys.version_info < (3, 8):
        pymalloc = sysconfig.get_config_var('WITH_PYMALLOC')
        if pymalloc or pymalloc is None:  # none is the default value, which is enable
            INTERPRETER_TAG += 'm'
elif platform.python_implementation() == 'PyPy':
    INTERPRETER_TAG = f'pypy3_{INTERPRETER_VERSION}'
    PYTHON_TAG = f'pp{INTERPRETER_VERSION}'
else:
    raise NotImplementedError(f'Unknown implementation: {platform.python_implementation()}')


if platform.system() == 'Linux':
    PLATFORM_TAG = f'linux_{platform.machine()}'
else:
    raise NotImplementedError(f'Unknown system: {platform.system()}')


def wheel_contents(artifact):
    # Sometimes directories have entries, sometimes not, so we filter them out.
    return {
        entry for entry in artifact.namelist()
        if not entry.endswith('/')
    }


def test_contents(package_library, wheel_library):
    artifact = wheel.wheelfile.WheelFile(wheel_library)

    for name, regex in zip(sorted(wheel_contents(artifact)), [
        re.escape('.library.mesonpy.libs/libexample.so'),
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


def test_interpreter_abi_tag(wheel_purelib_and_platlib):
    expected = f'purelib_and_platlib-1.0.0-{PYTHON_TAG}-{INTERPRETER_TAG}-{PLATFORM_TAG}.whl'
    assert wheel_purelib_and_platlib.name == expected


def test_local_lib(virtual_env, wheel_link_against_local_lib):
    subprocess.check_call([virtual_env, '-m', 'pip', 'install', wheel_link_against_local_lib])
    subprocess.check_output([
        virtual_env, '-c', 'import example; print(example.example_sum(1, 2))'
    ]).decode() == '3'
