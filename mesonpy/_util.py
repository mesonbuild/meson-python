# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import contextlib
import gzip
import itertools
import os
import sys
import tarfile
import typing

from typing import IO


if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import Any

    from mesonpy._compat import Iterator, Path, Self


@contextlib.contextmanager
def chdir(path: Path) -> Iterator[Path]:
    """Context manager helper to change the current working directory -- cd."""
    old_cwd = os.getcwd()
    os.chdir(os.fspath(path))
    try:
        yield path
    finally:
        os.chdir(old_cwd)


@contextlib.contextmanager
def create_targz(path: Path) -> Iterator[tarfile.TarFile]:
    """Opens a .tar.gz file in the file system for edition.."""

    os.makedirs(os.path.dirname(path), exist_ok=True)
    file = typing.cast(IO[bytes], gzip.GzipFile(
        path,
        mode='wb',
    ))
    tar = tarfile.TarFile(
        mode='w',
        fileobj=file,
        format=tarfile.PAX_FORMAT,  # changed in 3.8 to GNU
    )

    with contextlib.closing(file), tar:
        yield tar


class clicounter:
    def __init__(self, total: int) -> None:
        self._total = total
        self._count = itertools.count(start=1)

    def __enter__(self) -> Self:
        return self

    def update(self, description: str) -> None:
        line = f'[{next(self._count)}/{self._total}] {description}'
        if sys.stdout.isatty():
            print('\r', line, sep='', end='\33[0K', flush=True)
        else:
            print(line)

    def __exit__(self, exc_type: Any, exc_value: Any, exc_tb: Any) -> None:
        if sys.stdout.isatty():
            print()
