# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Lars Pastewka <lars.pastewka@imtek.uni-freiburg.de>

from __future__ import annotations

import os
import subprocess
import typing


if typing.TYPE_CHECKING:
    from typing import List, Optional

    from mesonpy._compat import Collection, Path


# This class is modeled after the ELF class in _elf.py
class Dylib:
    def __init__(self, path: Path) -> None:
        self._path = os.fspath(path)
        self._rpath: Optional[Collection[str]] = None
        self._load_dylib: Optional[Collection[str]] = None
        self._needed: Optional[Collection[str]] = None

    def _otool(self, *args: str) -> str:
        return subprocess.check_output(['otool', *args, self._path], stderr=subprocess.STDOUT).decode()

    def _install_name_tool(self, *args: str) -> str:
        return subprocess.check_output(['install_name_tool', *args, self._path], stderr=subprocess.STDOUT).decode()

    def _find_tag(self, name: str, field: str) -> List[str]:
        entries = []
        # Run otool -l to get the load commands
        otool_output = self._otool('-l').strip()
        # Manually parse the output and find the tag entries
        looking_at_tag = False
        for line in map(str.split, otool_output.splitlines()):
            if line[0] == 'cmd':
                if len(line) < 2:
                    raise ValueError('Unexpected "otool -l" output')
                looking_at_tag = line[1] == name
            elif looking_at_tag and line[0] == field:
                if len(line) < 2:
                    raise ValueError('Unexpected "otool -l" output')
                entries.append(line[1])
                looking_at_tag = False
        return entries

    @property
    def rpath(self) -> Collection[str]:
        if self._rpath is None:
            self._rpath = self._find_tag('LC_RPATH', 'path')
        return frozenset(self._rpath)

    @rpath.setter
    def rpath(self, value: Collection[str]) -> None:
        # We clear all LC_RPATH load commands
        if self._rpath:
            for rpath in self._rpath:
                self._install_name_tool('-delete_rpath', rpath)
        # We then rewrite the new load commands
        for rpath in value:
            self._install_name_tool('-add_rpath', rpath)
        self._rpath = value

    @property
    def load_dylib(self) -> Collection[str]:
        if self._load_dylib is None:
            self._load_dylib = self._find_tag('LC_LOAD_DYLIB', 'name')
        return frozenset(self._load_dylib)

    def replace_load_dylib(self, old: str, new: str) -> None:
        if old not in self.load_dylib:
            raise KeyError(f'LC_LOAD_DYLIB entry "{old}" not found')
        self._install_name_tool('-change', old, new)
        assert isinstance(self._load_dylib, list)
        self._load_dylib.remove(old)
        self._load_dylib.append(new)
