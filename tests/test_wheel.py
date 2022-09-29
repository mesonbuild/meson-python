# SPDX-License-Identifier: MIT

import os
import platform
import re
import subprocess
import sys
import sysconfig

import pytest
import wheel.wheelfile

import mesonpy._elf


try:
    import importlib.metadata  # not available in Python 3.7

    # Note, this may be None due to an importlib bug, handled in `finally`
    try:
        meson_version = importlib.metadata.version('meson')
    except importlib.metadata.PackageNotFoundError:
        meson_version = None
except ModuleNotFoundError:
    # Meson does not have to be installed in the same Python environment
    meson_version = None


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
    INTERPRETER_TAG = sysconfig.get_config_var('SOABI').replace('-', '_')
    PYTHON_TAG = f'pp{INTERPRETER_VERSION}'
else:
    raise NotImplementedError(f'Unknown implementation: {platform.python_implementation()}')

platform_ = sysconfig.get_platform()
if platform.system() == 'Darwin':
    parts = platform_.split('-')
    parts[1] = platform.mac_ver()[0]
    platform_ = '-'.join(parts)
PLATFORM_TAG = platform_.replace('-', '_').replace('.', '_')

if platform.system() == 'Linux':
    SHARED_LIB_EXT = 'so'
elif platform.system() == 'Darwin':
    SHARED_LIB_EXT = 'dylib'
elif platform.system() == 'Windows':
    SHARED_LIB_EXT = 'pyd'
else:
    raise NotImplementedError(f'Unknown system: {platform.system()}')


def wheel_contents(artifact):
    # Sometimes directories have entries, sometimes not, so we filter them out.
    return {
        entry for entry in artifact.namelist()
        if not entry.endswith('/')
    }


def wheel_filename(artifact):
    return artifact.filename.split(os.sep)[-1]


win_py37 = os.name == 'nt' and sys.version_info < (3, 8)


@pytest.mark.skipif(win_py37, reason='An issue with missing file extension')
def test_scipy_like(wheel_scipy_like):
    # This test is meant to exercise features commonly needed by a regular
    # Python package for scientific computing or data science:
    #   - C and Cython extensions,
    #   - including generated code,
    #   - using `install_subdir`,
    #   - packaging data files with extensions not known to Meson
    artifact = wheel.wheelfile.WheelFile(wheel_scipy_like)

    expecting = {
        'mypkg-2.3.4.dist-info/METADATA',
        'mypkg-2.3.4.dist-info/RECORD',
        'mypkg-2.3.4.dist-info/WHEEL',
        'mypkg/__init__.py',
        'mypkg/__config__.py',
        f'mypkg/extmod{EXT_SUFFIX}',
        f'mypkg/cy_extmod{EXT_SUFFIX}',
    }
    # Meson master has a fix for `install_subdir` that is not present in
    # 0.63.2: https://github.com/mesonbuild/meson/pull/10765
    # A backport of the fix may land in 0.63.3, if so then remove the version
    # check here and add the two expected files unconditionally.
    if meson_version and meson_version >= '0.63.99':
        expecting |= {
            'mypkg/submod/__init__.py',
            'mypkg/submod/unknown_filetype.npq',
        }
    if os.name == 'nt':
        # Currently Meson is installing `.dll.a` (import libraries) next to
        # `.pyd` extension modules. Those are very small, so it's not a major
        # issue - just sloppy. For now, ensure we don't fail on those
        actual_files = wheel_contents(artifact)
        for item in expecting:
            assert item in actual_files
    else:
        assert wheel_contents(artifact) == expecting

    name = artifact.parsed_filename
    assert name.group('pyver') == PYTHON_TAG
    assert name.group('abi') == INTERPRETER_TAG
    assert name.group('plat') == PLATFORM_TAG

    # Extra checks to doubly-ensure that there are no issues with erroneously
    # considering a package with an extension module as pure
    assert 'none' not in wheel_filename(artifact)
    assert 'any' not in wheel_filename(artifact)


@pytest.mark.skipif(platform.system() != 'Linux', reason='Needs library vendoring, only implemented in POSIX')
def test_contents(package_library, wheel_library):
    artifact = wheel.wheelfile.WheelFile(wheel_library)

    for name, regex in zip(sorted(wheel_contents(artifact)), [
        re.escape(f'.library.mesonpy.libs/libexample.{SHARED_LIB_EXT}'),
        re.escape('library-1.0.0.data/headers/examplelib.h'),
        re.escape('library-1.0.0.data/scripts/example'),
        re.escape('library-1.0.0.dist-info/METADATA'),
        re.escape('library-1.0.0.dist-info/RECORD'),
        re.escape('library-1.0.0.dist-info/WHEEL'),
        rf'library\.libs/libexample.*\.{SHARED_LIB_EXT}',
    ]):
        assert re.match(regex, name), f'`{name}` does not match `{regex}`'


@pytest.mark.skipif(win_py37,
                    reason='Somehow pkg-config went missing within Nox env, see gh-145')
@pytest.mark.xfail(meson_version and meson_version < '0.63.99', reason='Meson bug')
def test_purelib_and_platlib(wheel_purelib_and_platlib):
    artifact = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib)

    expecting = {
        f'plat{EXT_SUFFIX}',
        'purelib_and_platlib-1.0.0.data/purelib/pure.py',
        'purelib_and_platlib-1.0.0.dist-info/METADATA',
        'purelib_and_platlib-1.0.0.dist-info/RECORD',
        'purelib_and_platlib-1.0.0.dist-info/WHEEL',
    }
    if platform.system() == 'Windows':
        expecting.add('plat{}'.format(EXT_SUFFIX.replace('pyd', 'dll.a')))

    assert wheel_contents(artifact) == expecting


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
        'configure_data.py',
        'configure_data-1.0.0.dist-info/METADATA',
        'configure_data-1.0.0.dist-info/RECORD',
        'configure_data-1.0.0.dist-info/WHEEL',
    }


@pytest.mark.xfail(reason='Meson bug')
def test_interpreter_abi_tag(wheel_purelib_and_platlib):
    expected = f'purelib_and_platlib-1.0.0-{PYTHON_TAG}-{INTERPRETER_TAG}-{PLATFORM_TAG}.whl'
    assert wheel_purelib_and_platlib.name == expected


@pytest.mark.skipif(platform.system() != 'Linux', reason='Unsupported on this platform for now')
@pytest.mark.xfail(
    (
        (sys.version_info >= (3, 9) or platform.python_implementation() == 'PyPy')
        and os.environ.get('GITHUB_ACTIONS') == 'true'
    ),
    reason='github actions',
    strict=True,
)
def test_local_lib(virtual_env, wheel_link_against_local_lib):
    subprocess.check_call([virtual_env, '-m', 'pip', 'install', wheel_link_against_local_lib])
    assert subprocess.check_output([
        virtual_env, '-c', 'import example; print(example.example_sum(1, 2))'
    ]).decode().strip() == '3'


def test_contents_license_file(wheel_license_file):
    artifact = wheel.wheelfile.WheelFile(wheel_license_file)
    assert artifact.read('license_file-1.0.0.dist-info/LICENSE.custom').rstrip() == b'Hello!'


@pytest.mark.skipif(os.name == 'nt', reason='Executable bit does not exist on Windows')
def test_executable_bit(wheel_executable_bit):
    artifact = wheel.wheelfile.WheelFile(wheel_executable_bit)

    # With Meson 0.63.x we see `data/bin/`, with master `scripts/`. The latter
    # seems correct - see gh-115 for more details.
    executable_files = {
        'executable_bit-1.0.0.data/purelib/executable_module.py',
        'executable_bit-1.0.0.data/scripts/example',
        'executable_bit-1.0.0.data/scripts/example-script',
        'executable_bit-1.0.0.data/data/bin/example-script',
    }

    for info in artifact.infolist():
        mode = (info.external_attr >> 16) & 0o777
        executable_bit = bool(mode & 0b001_000_000)  # owner execute
        if info.filename in executable_files:
            assert executable_bit, f'{info.filename} should have the executable bit set!'
        else:
            assert not executable_bit, f'{info.filename} should not have the executable bit set!'


@pytest.mark.skipif(os.name == 'nt',
                    reason='Wheel build fixture in conftest.py broken on Windows')
def test_detect_wheel_tag_module(wheel_purelib_and_platlib):
    name = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib).parsed_filename
    assert name.group('pyver') == PYTHON_TAG
    assert name.group('abi') == INTERPRETER_TAG
    assert name.group('plat') == PLATFORM_TAG.replace('-', '_').replace('.', '_')


def test_detect_wheel_tag_script(wheel_executable):
    name = wheel.wheelfile.WheelFile(wheel_executable).parsed_filename
    assert name.group('pyver') == 'py3'
    assert name.group('abi') == 'none'
    assert name.group('plat') == PLATFORM_TAG.replace('-', '_').replace('.', '_')


@pytest.mark.skipif(platform.system() != 'Linux', reason='Unsupported on this platform for now')
def test_rpath(wheel_link_against_local_lib, tmpdir):
    artifact = wheel.wheelfile.WheelFile(wheel_link_against_local_lib)
    artifact.extractall(tmpdir)

    elf = mesonpy._elf.ELF(tmpdir / f'example{EXT_SUFFIX}')
    assert '$ORIGIN/.link_against_local_lib.mesonpy.libs' in elf.rpath


@pytest.mark.skipif(platform.system() != 'Linux', reason='Unsupported on this platform for now')
def test_uneeded_rpath(wheel_purelib_and_platlib, tmpdir):
    artifact = wheel.wheelfile.WheelFile(wheel_purelib_and_platlib)
    artifact.extractall(tmpdir)

    elf = mesonpy._elf.ELF(tmpdir / f'plat{EXT_SUFFIX}')
    if elf.rpath:
        # elf.rpath is a frozenset, so iterate over it. An rpath may be
        # present, e.g. when conda is used (rpath will be <conda-prefix>/lib/)
        for rpath in elf.rpath:
            assert 'mesonpy.libs' not in rpath
