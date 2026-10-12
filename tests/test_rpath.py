# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import pathlib
import sys

import pytest
import wheel.wheelfile

import mesonpy

from mesonpy._rpath import RPATH, get_rpath, set_rpath


@pytest.mark.skipif(sys.platform in {'win32', 'cygwin'}, reason='requires RPATH support')
def test_rpath_get_set(wheel_sharedlib_in_package, tmp_path):
    artifact = wheel.wheelfile.WheelFile(wheel_sharedlib_in_package)
    artifact.extractall(tmp_path)
    obj = list(tmp_path.joinpath('mypkg').glob('_example.*'))[0]

    rpath = get_rpath(obj)
    assert rpath

    set_rpath(obj, rpath, [])
    rpath = get_rpath(obj)
    assert rpath == []

    new_rpath = ['one', 'two']
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert rpath == new_rpath

    new_rpath = ['one', 'three', 'two']
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert rpath == new_rpath

    new_rpath = ['one']
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert rpath == new_rpath

    new_rpath = [
        'with two  or three   spaces',
        'trailing space ',
        '/some funny absolute path/(library)',
        '@loader_path/Mach-O relative',
        '$ORIGIN/ELF relative',
    ]
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert rpath == new_rpath

    new_rpath = ['alpha', 'beta']
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert rpath == new_rpath


def test_fix_rpath():
    calls = []

    class DummyRPATH(RPATH):
        @staticmethod
        def get_rpath(filepath):
            return ['$ORIGIN/old', 'build/dir', 'XXXXX']

        @staticmethod
        def set_rpath(filepath, old, rpath):
            calls.append((filepath, old, rpath))

    install_rpath = ['$ORIGIN/custom']
    build_rpath = ['build/dir']
    DummyRPATH.fix_rpath('dummy', install_rpath, build_rpath, 'libs')

    expected_new = ['$ORIGIN/custom', '$ORIGIN/old', os.path.join('$ORIGIN', 'libs')]
    assert calls == [('dummy', ['$ORIGIN/old', 'build/dir', 'XXXXX'], expected_new)]


def test_fix_rpath_sequence():
    calls = []

    class DummyRPATH(RPATH):
        @staticmethod
        def get_rpath(filepath):
            return ['$ORIGIN/old']

        @staticmethod
        def set_rpath(filepath, old, rpath):
            calls.append(rpath)

    DummyRPATH.fix_rpath('dummy', ('$ORIGIN/custom',), (), None)
    assert calls == [['$ORIGIN/custom', '$ORIGIN/old']]


def test_entry_default():
    entry = mesonpy._Entry(pathlib.Path('dst'), 'src')
    assert entry.install_rpath == ()
    assert entry.build_rpath == ()
