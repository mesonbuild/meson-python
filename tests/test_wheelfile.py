import time

import wheel.wheelfile

import mesonpy._wheelfile


def test_basic(tmp_path):
    path = tmp_path / 'test-1.0-py3-any-none.whl'
    bar = tmp_path / 'bar'
    open(bar, 'wb').write(b'bar')
    with mesonpy._wheelfile.WheelFile(path, 'w') as w:
        assert w.name == 'test'
        assert w.version == '1.0'
        w.writestr('foo', b'test')
        w.write(bar, 'bar')
    with wheel.wheelfile.WheelFile(path, 'r') as w:
        assert set(w.namelist()) == {'foo', 'bar', 'test-1.0.dist-info/RECORD'}
        w.open('foo').read() == b'test'
        w.open('bar').read() == b'bar'


def test_source_date_epoch(tmp_path, monkeypatch):
    path = tmp_path / 'test-1.0-py3-any-none.whl'
    epoch = 1668871912
    # The ZIP file format timestamps have 2 seconds resolution.
    assert epoch % 2 == 0
    monkeypatch.setenv('SOURCE_DATE_EPOCH', str(epoch))
    bar = tmp_path / 'bar'
    open(bar, 'wb').write(b'bar')
    with mesonpy._wheelfile.WheelFile(path, 'w') as w:
        w.writestr('foo', b'test')
        w.write(bar, 'bar')
    with wheel.wheelfile.WheelFile(path, 'r') as w:
        for entry in w.infolist():
            assert entry.date_time == time.gmtime(epoch)[:6]
