# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

import sys

import pytest
import wheel.wheelfile

from mesonpy._rpath import get_rpath, set_rpath


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
    assert set(rpath) == set(new_rpath)

    new_rpath = ['one', 'three', 'two']
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert set(rpath) == set(new_rpath)

    new_rpath = ['one']
    set_rpath(obj, rpath, new_rpath)
    rpath = get_rpath(obj)
    assert set(rpath) == set(new_rpath)
