# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import pathlib


def data():
    with pathlib.Path(__file__).parent.joinpath('data.txt').open() as f:
        return f.read().rstrip()
