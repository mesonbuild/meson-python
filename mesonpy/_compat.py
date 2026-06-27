# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import typing


if typing.TYPE_CHECKING:
    from typing import Union

    Path = Union[str, os.PathLike[str]]


__all__ = [
    'Path',
]
