# SPDX-License-Identifier: MIT

import importlib

import pytest

import mesonpy


@pytest.fixture()
def reload_module():
    try:
        yield
    finally:
        importlib.reload(mesonpy)


@pytest.mark.parametrize(
    ('tty', 'env', 'colors'),
    [
        (False, {}, False),
        (True, {}, True),
        (False, {'NO_COLOR': ''}, False),
        (True, {'NO_COLOR': ''}, False),
        (False, {'FORCE_COLOR': ''}, True),
        (True, {'FORCE_COLOR': ''}, True),
    ],
)
def test_colors(mocker, monkeypatch, reload_module, tty, env, colors):
    mocker.patch('sys.stdout.isatty', return_value=tty)
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    importlib.reload(mesonpy)  # reload module to set _STYLES

    assert mesonpy._STYLES == (mesonpy._COLORS if colors else mesonpy._NO_COLORS)


def test_colors_conflict(monkeypatch, reload_module):
    with monkeypatch.context() as m:
        m.setenv('NO_COLOR', '')
        m.setenv('FORCE_COLOR', '')

        with pytest.warns(
            UserWarning,
            match='Both NO_COLOR and FORCE_COLOR environment variables are set, disabling color',
        ):
            importlib.reload(mesonpy)

        assert mesonpy._STYLES == mesonpy._NO_COLORS
