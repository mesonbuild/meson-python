# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

import contextlib
import time
import zipfile

import pytest
import wheel.wheelfile

import mesonpy._wheelfile


def test_basic(tmp_path):
    path = tmp_path / 'test-1.0-py3-any-none.whl'
    bar = tmp_path / 'bar'
    bar.write_bytes(b'bar')
    with mesonpy._wheelfile.WheelFile(path, 'w') as w:
        assert w.name == 'test'
        assert w.version == '1.0'
        w.writestr('foo', b'test')
        w.write(bar, 'bar')
    with contextlib.closing(wheel.wheelfile.WheelFile(path, 'r')) as w:
        assert set(w.namelist()) == {'foo', 'bar', 'test-1.0.dist-info/RECORD'}
        with w.open('foo') as foo:
            assert foo.read() == b'test'
        with w.open('bar') as bar:
            assert bar.read() == b'bar'


def test_source_date_epoch(tmp_path, monkeypatch):
    path = tmp_path / 'test-1.0-py3-any-none.whl'
    epoch = 1668871912
    # The ZIP file format timestamps have 2 seconds resolution.
    assert epoch % 2 == 0
    monkeypatch.setenv('SOURCE_DATE_EPOCH', str(epoch))
    bar = tmp_path / 'bar'
    bar.write_bytes(b'bar')
    with mesonpy._wheelfile.WheelFile(path, 'w') as w:
        w.writestr('foo', b'test')
        w.write(bar, 'bar')
    with wheel.wheelfile.WheelFile(path, 'r') as w:
        for entry in w.infolist():
            assert entry.date_time == time.gmtime(epoch)[:6]


@pytest.mark.parametrize('mtime', [0, 283993200, 1668871912])
def test_timestamp(monkeypatch, mtime):
    monkeypatch.delenv('SOURCE_DATE_EPOCH', raising=False)
    assert mesonpy._wheelfile.WheelFile.timestamp(mtime) == max(time.gmtime(mtime)[:6], (1980, 1, 1, 0, 0, 0))


def test_compression(tmp_path):
    # create a wheel and test that everything is compressed
    path = tmp_path / 'test-1.0-py3-any-none.whl'
    bar = tmp_path / 'bar'
    bar.write_bytes(b'bar')
    with mesonpy._wheelfile.WheelFile(path, 'w') as w:
        w.writestr('foo', b'test')
        w.write(bar, 'bar')
    with zipfile.ZipFile(path, 'r') as w:
        for entry in w.infolist():
            assert entry.compress_type == zipfile.ZIP_DEFLATED
