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

    if sys.version_info >= (3, 10):
        from typing import ParamSpec
    else:
        from typing_extensions import ParamSpec

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

    Path = Union[str, os.PathLike[str]]


__all__ = [
    'Path',
    'ParamSpec',
    'Self',
]
