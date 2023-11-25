# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import pytest

import mesonpy


@pytest.mark.parametrize(('tty', 'env', 'colors'), [
    (False, {}, False),
    (True, {}, True),
    (False, {'NO_COLOR': ''}, False),
    (True, {'NO_COLOR': ''}, False),
    (False, {'FORCE_COLOR': ''}, True),
    (True, {'FORCE_COLOR': ''}, True),
    (True, {'FORCE_COLOR': '', 'NO_COLOR': ''}, False),
    (True, {'TERM': ''}, True),
    (True, {'TERM': 'dumb'}, False),
])
def test_use_ansi_escapes(mocker, monkeypatch, tty, env, colors):
    mocker.patch('sys.stdout.isatty', return_value=tty)
    mocker.patch('mesonpy._util.setup_windows_console', return_value=True)
    monkeypatch.delenv('NO_COLOR', raising=False)
    monkeypatch.delenv('FORCE_COLOR', raising=False)
    for key, value in env.items():
        monkeypatch.setenv(key, value)

    # Clear caching by functools.lru_cache().
    mesonpy._use_ansi_escapes.cache_clear()

    assert mesonpy._use_ansi_escapes() == colors
