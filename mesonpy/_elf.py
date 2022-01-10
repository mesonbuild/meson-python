# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>

import os
import subprocess

from typing import Optional

from mesonpy._compat import Collection, Path


class ELF:
    def __init__(self, path: Path) -> None:
        self._path = os.fspath(path)
        self._rpath: Optional[Collection[str]] = None
        self._needed: Optional[Collection[str]] = None

    def _patchelf(self, *args: str) -> str:
        return subprocess.check_output(['patchelf', *args, self._path]).decode()

    @property
    def rpath(self) -> Collection[str]:
        if not self._rpath:
            self._rpath = self._patchelf('--print-rpath').strip().split(';')
        return self._rpath

    @rpath.setter
    def rpath(self, value: Collection[str]) -> None:
        self._patchelf('--set-rpath', ':'.join(value))
        self._rpath = value

    @property
    def needed(self) -> Collection[str]:
        if self._needed is None:
            self._needed = frozenset(self._patchelf('--print-needed').splitlines())
        return self._needed

    @needed.setter
    def needed(self, value: Collection[str]) -> None:
        value = frozenset(value)
        for entry in self.needed:
            if entry not in value:
                self._patchelf('--remove-needed', entry)
        for entry in value:
            if entry not in self.needed:
                self._patchelf('--add-needed', entry)
        self._needed = value
