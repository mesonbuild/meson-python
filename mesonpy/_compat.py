# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>

import os
import pathlib
import sys

from typing import Union


if sys.version_info >= (3, 9):
    from collections.abc import (
        Collection, Iterable, Iterator, Mapping, Sequence
    )
else:
    from typing import Collection, Iterable, Iterator, Mapping, Sequence


if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


Path = Union[str, os.PathLike]


# backport og pathlib.Path.is_relative_to
def is_relative_to(path: pathlib.Path, other: Union[pathlib.Path, str]) -> bool:
    try:
        path.relative_to(other)
    except ValueError:
        return False
    return True


__all__ = [
    'is_relative_to',
    'Collection',
    'Iterable',
    'Iterator',
    'Literal',
    'Mapping',
    'Path',
    'Sequence',
]
