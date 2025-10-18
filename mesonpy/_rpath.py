# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import re
import subprocess
import sys
import typing


if typing.TYPE_CHECKING:
    Path = str | os.PathLike[str]
    T = typing.TypeVar('T')


def unique(values: list[T]) -> list[T]:
    return list(dict.fromkeys(values))


class RPATH:

    origin = '$ORIGIN'

    @staticmethod
    def get_rpath(filepath: Path) -> list[str]:
        raise NotImplementedError

    @staticmethod
    def set_rpath(filepath: Path, old: list[str], rpath: list[str]) -> None:
        raise NotImplementedError

    @classmethod
    def fix_rpath(cls, filepath: Path, install_rpath: list[str], libs_relative_path: str | None) -> None:
        old_rpath = cls.get_rpath(filepath)

        # Prepend install_rpath entries.
        new_rpath = install_rpath + old_rpath

        # When an executable, library, or Python extension module is
        # dynamically linked to a library built as part of the project, Meson
        # adds a build RPATH pointing to the build directory, in the form of a
        # relative RPATH entry. We can use the presence of any RPATH entries
        # relative to ``$ORIGIN`` as an indicator that the installed object
        # depends on shared libraries internal to the project. In this case we
        # need to add an RPATH entry pointing to the meson-python shared
        # library install location. This heuristic is not perfect: RPATH
        # entries relative to ``$ORIGIN`` can exist for other reasons.
        # However, this only results in harmless additional RPATH entries.
        if libs_relative_path and any(path.startswith(cls.origin) for path in old_rpath):
            new_rpath.append(os.path.join(cls.origin, libs_relative_path))

        new_rpath = unique(new_rpath)
        if new_rpath != old_rpath:
            cls.set_rpath(filepath, old_rpath, new_rpath)


class _Windows(RPATH):

    @classmethod
    def fix_rpath(cls, filepath: Path, install_rpath: list[str], libs_relative_path: str) -> None:
        pass


class _MacOS(RPATH):

    origin = '@loader_path'

    @staticmethod
    def get_rpath(filepath: Path) -> list[str]:
        rpath = []
        r = subprocess.run(['otool', '-l', os.fspath(filepath)], capture_output=True, text=True)
        lines = iter(r.stdout.splitlines())
        for line in lines:
            if line.strip().startswith('cmd LC_RPATH'):
                for line in lines:
                    if m := re.match(r'^\s*path (.+) \(offset \d+\)$', line):
                        rpath.append(m.group(1))
                        break
        return rpath

    @staticmethod
    def set_rpath(filepath: Path, old: list[str], rpath: list[str]) -> None:
        # ``install_name_tool`` allows to delete, add, or rewrite specific
        # LC_RPATH entries, however, this operations cannot be combined in
        # arbitrary order in a single call.  The only robust way to get
        # entries in a specific order with at max two tool invocations is to
        # delete the entries that are out of place and re-add them in the
        # right order.

        keep = 0
        while keep < len(old) and keep < len(rpath) and old[keep] == rpath[keep]:
            keep += 1

        delete = old[keep:]
        add = rpath[keep:]

        if delete:
            args = [a for p in delete for a in ('-delete_rpath', p)]
            subprocess.run(['install_name_tool', *args, os.fspath(filepath)], check=True)

        if add:
            args = [a for p in add for a in ('-add_rpath', p)]
            subprocess.run(['install_name_tool', *args, os.fspath(filepath)], check=True)


class _SunOS5(RPATH):

    @staticmethod
    def get_rpath(filepath: Path) -> list[str]:
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
    def set_rpath(filepath: Path, old: list[str], rpath: list[str]) -> None:
        subprocess.run(['/usr/bin/elfedit', '-e', 'dyn:rpath ' + ':'.join(rpath), os.fspath(filepath)], check=True)


class _ELF(RPATH):

    @staticmethod
    def get_rpath(filepath: Path) -> list[str]:
        r = subprocess.run(['patchelf', '--print-rpath', os.fspath(filepath)], capture_output=True, text=True)
        return [x for x in r.stdout.strip().split(':') if x]

    @staticmethod
    def set_rpath(filepath: Path, old: list[str], rpath: list[str]) -> None:
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
