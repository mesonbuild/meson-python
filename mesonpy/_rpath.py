# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import subprocess
import sys
import typing


if typing.TYPE_CHECKING:
    from typing import List, Optional, TypeVar

    from mesonpy._compat import Iterable, Path

    T = TypeVar('T')


def unique(values: List[T]) -> List[T]:
    r = []
    for value in values:
        if value not in r:
            r.append(value)
    return r


class _Windows:

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        return []

    @classmethod
    def fix_rpath(cls, filepath: Path, install_rpath: Optional[str], libs_rpath: Optional[str]) -> None:
        pass


class RPATH:
    origin = '$ORIGIN'

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        raise NotImplementedError

    @staticmethod
    def set_rpath(filepath: Path, old: List[str], rpath: List[str]) -> None:
        raise NotImplementedError

    @classmethod
    def fix_rpath(cls, filepath: Path, install_rpath: Optional[str], libs_rpath: Optional[str]) -> None:
        old_rpath = cls.get_rpath(filepath)
        new_rpath = []
        if libs_rpath is not None:
            if libs_rpath == '.':
                libs_rpath = ''
            for path in old_rpath:
                if path.split('/', 1)[0] == cls.origin:
                    # Any RPATH entry relative to ``$ORIGIN`` is interpreted as
                    # pointing to a location in the build directory added by
                    # Meson. These need to be removed. Their presence indicates
                    # that the executable, shared library, or Python module
                    # depends on libraries build as part of the package. These
                    # entries are thus replaced with entries pointing to the
                    # ``.<package-name>.mesonpy.libs`` folder where meson-python
                    # relocates shared libraries distributed with the package.
                    # The package may however explicitly install these in a
                    # different location, thus this is not a perfect heuristic
                    # and may add not required RPATH entries. These are however
                    # harmless.
                    path = f'{cls.origin}/{libs_rpath}'
                # Any other RPATH entry is preserved.
                new_rpath.append(path)
        if install_rpath:
            # Add the RPATH entry spcified with the ``install_rpath`` argument.
            new_rpath.append(install_rpath)
        # Make the RPATH entries unique.
        new_rpath = unique(new_rpath)
        if new_rpath != old_rpath:
            cls.set_rpath(filepath, old_rpath, new_rpath)


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
        args: List[str] = []
        for path in rpath:
            if path not in old:
                args += ['-add_rpath', path]
        for path in old:
            if path not in rpath:
                args += ['-delete_rpath', path]
        subprocess.run(['install_name_tool', *args, os.fspath(filepath)], check=True)

    @classmethod
    def fix_rpath(cls, filepath: Path, install_rpath: Optional[str], libs_rpath: Optional[str]) -> None:
        if install_rpath is not None:
            root, sep, stem = install_rpath.partition('/')
            if root == '$ORIGIN':
                install_rpath = f'{cls.origin}{sep}{stem}'
                # warnings.warn('...')
        super().fix_rpath(filepath, install_rpath, libs_rpath)


class _SunOS(RPATH):

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
    def set_rpath(filepath: Path, old: Iterable[str], rpath: Iterable[str]) -> None:
        subprocess.run(['/usr/bin/elfedit', '-e', 'dyn:rpath ' + ':'.join(rpath), os.fspath(filepath)], check=True)


class _ELF(RPATH):

    @staticmethod
    def get_rpath(filepath: Path) -> List[str]:
        r = subprocess.run(['patchelf', '--print-rpath', os.fspath(filepath)], capture_output=True, text=True)
        return r.stdout.strip().split(':')

    @staticmethod
    def set_rpath(filepath: Path, old: Iterable[str], rpath: Iterable[str]) -> None:
        subprocess.run(['patchelf','--set-rpath', ':'.join(rpath), os.fspath(filepath)], check=True)


if sys.platform == 'win32' or sys.platform == 'cygwin':
    _cls = _Windows
elif sys.platform == 'darwin':
    _cls = _MacOS
elif sys.platform == 'sunos5':
    _cls = _SunOS
else:
    _cls = _ELF

_get_rpath = _cls.get_rpath
fix_rpath = _cls.fix_rpath
