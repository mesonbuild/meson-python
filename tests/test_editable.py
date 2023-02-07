# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os

import mesonpy


def test_editable(
    package_imports_itself_during_build,
    editable_imports_itself_during_build,
    venv,
):
    venv.pip('install', os.fspath(editable_imports_itself_during_build))

    assert venv.python('-c', 'import plat; print(plat.foo())').strip() == 'bar'

    plat = package_imports_itself_during_build / 'plat.c'
    plat_text = plat.read_text()
    try:
        plat.write_text(plat_text.replace('bar', 'something else'))

        assert venv.python('-c', 'import plat; print(plat.foo())').strip() == 'something else'
    finally:
        plat.write_text(plat_text)


