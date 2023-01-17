# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>

import contextlib
import gzip
import os
import sys
import tarfile
import typing

from typing import IO, Optional, Tuple

from mesonpy._compat import Iterable, Iterator, Path


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
def add_ld_path(paths: Iterable[str]) -> Iterator[None]:
    """Context manager helper to add a path to LD_LIBRARY_PATH."""
    old_value = os.environ.get('LD_LIBRARY_PATH')
    old_paths = old_value.split(os.pathsep) if old_value else []
    os.environ['LD_LIBRARY_PATH'] = os.pathsep.join([*paths, *old_paths])
    try:
        yield
    finally:
        if old_value is not None:  # pragma: no cover
            os.environ['LD_LIBRARY_PATH'] = old_value


@contextlib.contextmanager
def create_targz(path: Path) -> Iterator[Tuple[tarfile.TarFile, Optional[int]]]:
    """Opens a .tar.gz file in the file system for edition.."""

    # reproducibility
    source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH')
    mtime = int(source_date_epoch) if source_date_epoch else None

    file = typing.cast(IO[bytes], gzip.GzipFile(
        path,
        mode='wb',
        mtime=mtime,
    ))
    tar = tarfile.TarFile(
        mode='w',
        fileobj=file,
        format=tarfile.PAX_FORMAT,  # changed in 3.8 to GNU
    )

    with contextlib.closing(file), tar:
        yield tar, mtime


class CLICounter:
    def __init__(self, total: int) -> None:
        self._total = total - 1
        self._count = -1
        self._current_line = ''

    def update(self, description: str) -> None:
        self._count += 1
        new_line = f'[{self._count}/{self._total}] {description}'
        if sys.stdout.isatty():
            pad_size = abs(len(self._current_line) - len(new_line))
            print(' ' + new_line + ' ' * pad_size, end='\r', flush=True)
        else:
            print(new_line)
        self._current_line = new_line

    def finish(self) -> None:
        if sys.stdout.isatty():
            print(f'\r{self._current_line}')


@contextlib.contextmanager
def cli_counter(total: int) -> Iterator[CLICounter]:
    counter = CLICounter(total)
    yield counter
    counter.finish()
