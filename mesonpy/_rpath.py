# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import subprocess
import sys
import typing


if typing.TYPE_CHECKING:
    from typing import List, TypeVar

    from mesonpy._compat import Path

    T = TypeVar('T')


def unique(values: List[T]) -> List[T]:
    r = []
    for value in values:
        if value not in r:
            r.append(value)
    return r


class RPATH:

    origin = '$ORIGIN'

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        raise NotImplementedError

    @staticmethod
    def set_rpath(filepath: Path, old: List[str], rpath: List[str]) -> None:
        raise NotImplementedError

    @classmethod
    def fix_rpath(cls, filepath: Path, libs_relative_path: str) -> None:
        old_rpath = cls.get_rpath(filepath)
        new_rpath = old_rpath[:]

        # When an executable, libray, or Python extension module is
        # dynamically linked to a library built as part of the project, Meson
        # adds a build RPATH pointing to the build directory, in the form of a
        # relative RPATH entry. We can use the presence of any RPATH entries
        # relative to ``$ORIGIN`` as an indicator that the installed object
        # depends on shared libraries internal to the project. In this case we
        # need to add an RPATH entry pointing to the meson-python shared
        # library install location. This heuristic is not perfect: RPATH
        # entries relative to ``$ORIGIN`` can exist for other reasons.
        # However, this only results in harmless additional RPATH entries.
        if any(path.startswith(cls.origin) for path in old_rpath):
            new_rpath.append(os.path.join(cls.origin, libs_relative_path))

        new_rpath = unique(new_rpath)
        if new_rpath != old_rpath:
            cls.set_rpath(filepath, old_rpath, new_rpath)


class _Windows(RPATH):

    @classmethod
    def fix_rpath(cls, filepath: Path, libs_relative_path: str) -> None:
        pass


class _MacOS(RPATH):

    origin = '@loader_path'

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        rpath = []
        r = subprocess.run(['otool', '-l', os.fspath(filepath)], capture_output=True, text=True)
        rpath_tag = False
        for line in [x.split() for x in r.stdout.split('\n')]:
            if line == ['cmd', 'LC_RPATH']:
                rpath_tag = True
            elif len(line) >= 2 and line[0] == 'path' and rpath_tag:
                rpath.append(line[1])
                rpath_tag = False
        return rpath

    @staticmethod
    def set_rpath(filepath: Path, old: List[str], rpath: List[str]) -> None:
        # This implementation does not preserve the ordering of RPATH
        # entries. Meson does the same, thus it should not be a problem.
        args: List[str] = []
        for path in rpath:
            if path not in old:
                args += ['-add_rpath', path]
        for path in old:
            if path not in rpath:
                args += ['-delete_rpath', path]
        subprocess.run(['install_name_tool', *args, os.fspath(filepath)], check=True)


class _SunOS5(RPATH):

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        rpath = []
        r = subprocess.run(['/usr/bin/elfedit', '-r', '-e', 'dyn:rpath', os.fspath(filepath)],
            capture_output=True, check=True, text=True)
        for line in [x.split() for x in r.stdout.split('\n')]:
            if len(line) >= 4 and line[1] in ['RPATH', 'RUNPATH']:
                for path in line[3].split(':'):
                    if path not in rpath:
                        rpath.append(path)
        return rpath

    @staticmethod
    def set_rpath(filepath: Path, old: List[str], rpath: List[str]) -> None:
        subprocess.run(['/usr/bin/elfedit', '-e', 'dyn:rpath ' + ':'.join(rpath), os.fspath(filepath)], check=True)


class _ELF(RPATH):

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        r = subprocess.run(['patchelf', '--print-rpath', os.fspath(filepath)], capture_output=True, text=True)
        return [x for x in r.stdout.strip().split(':') if x]

    @staticmethod
    def set_rpath(filepath: Path, old: List[str], rpath: List[str]) -> None:
        subprocess.run(['patchelf','--set-rpath', ':'.join(rpath), os.fspath(filepath)], check=True)


if sys.platform == 'win32' or sys.platform == 'cygwin':
    _cls = _Windows
elif sys.platform == 'darwin':
    _cls = _MacOS
elif sys.platform == 'sunos5':
    _cls = _SunOS5
else:
    _cls = _ELF

get_rpath = _cls.get_rpath
set_rpath = _cls.set_rpath
fix_rpath = _cls.fix_rpath
