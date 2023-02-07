# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

# This file should be standalone! It is copied during the editable hook installation.

from __future__ import annotations

import functools
import importlib.abc
import importlib.machinery
import importlib.util
import json
import os
import pathlib
import subprocess
import sys
import typing


if typing.TYPE_CHECKING:
    from collections.abc import Sequence, Set
    from types import ModuleType
    from typing import Any, Dict, Iterator, List, Optional, Tuple, Union
    NodeBase = Dict[str, Union[Node, str]]
else:
    NodeBase = dict


MARKER = 'MESONPY_EDITABLE_SKIP'
VERBOSE = 'MESONPY_EDITABLE_VERBOSE'

LOADERS = [
    (importlib.machinery.ExtensionFileLoader, tuple(importlib.machinery.EXTENSION_SUFFIXES)),
    (importlib.machinery.SourceFileLoader, tuple(importlib.machinery.SOURCE_SUFFIXES)),
    (importlib.machinery.SourcelessFileLoader, tuple(importlib.machinery.BYTECODE_SUFFIXES)),
]


class Node(NodeBase):
    """Tree structure to store a virtual filesystem view."""

    def __missing__(self, key: str) -> Node:
        value = self[key] = Node()
        return value

    def __setitem__(self, key: Union[str, Tuple[str, ...]], value: Union[Node, str]) -> None:
        node = self
        if isinstance(key, tuple):
            for k in key[:-1]:
                node = typing.cast(Node, node[k])
            key = key[-1]
        dict.__setitem__(node, key, value)

    def __getitem__(self, key: Union[str, Tuple[str, ...]]) -> Union[Node, str]:
        node = self
        if isinstance(key, tuple):
            for k in key[:-1]:
                node = typing.cast(Node, node[k])
            key = key[-1]
        return dict.__getitem__(node, key)

    def get(self, key: Union[str, Tuple[str, ...]]) -> Optional[Union[Node, str]]:  # type: ignore[override]
        node = self
        if isinstance(key, tuple):
            for k in key[:-1]:
                v = dict.get(node, k)
                if v is None:
                    return None
                node = typing.cast(Node, v)
            key = key[-1]
        return dict.get(node, key)


def walk(root: str, path: str = '') -> Iterator[pathlib.Path]:
    with os.scandir(os.path.join(root, path)) as entries:
        for entry in entries:
            if entry.is_dir():
                yield from walk(root, os.path.join(path, entry.name))
            else:
                yield pathlib.Path(path, entry.name)


def collect(install_plan: Dict[str, Dict[str, Any]]) -> Node:
    tree = Node()
    for key, data in install_plan.items():
        for src, target in data.items():
            path = pathlib.Path(target['destination'])
            if path.parts[0] in {'{py_platlib}', '{py_purelib}'}:
                if key == 'install_subdirs' and os.path.isdir(src):
                    for entry in walk(src):
                        tree[(*path.parts[1:], *entry.parts)] = os.path.join(src, *entry.parts)
                else:
                    tree[path.parts[1:]] = src
    return tree


class MesonpyMetaFinder(importlib.abc.MetaPathFinder):
    def __init__(self, names: Set[str], path: str, cmd: List[str], verbose: bool = False):
        self._top_level_modules = names
        self._build_path = path
        self._build_cmd = cmd
        self._verbose = verbose
        self._loaders: List[Tuple[type, str]] = []
        for loader, suffixes in LOADERS:
            self._loaders.extend((loader, suffix) for suffix in suffixes)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._build_path!r})'

    def find_spec(
            self,
            fullname: str,
            path: Optional[Sequence[Union[bytes, str]]] = None,
            target: Optional[ModuleType] = None
    ) -> Optional[importlib.machinery.ModuleSpec]:
        if fullname.split('.', maxsplit=1)[0] in self._top_level_modules:
            if self._build_path in os.environ.get(MARKER, '').split(os.pathsep):
                return None
            namespace = False
            tree = self.rebuild()
            parts = fullname.split('.')

            # look for a package
            package = tree.get(tuple(parts))
            if isinstance(package, Node):
                for loader, suffix in self._loaders:
                    src = package.get('__init__' + suffix)
                    if isinstance(src, str):
                        return build_module_spec(loader, fullname, src, package)
                else:
                    namespace = True

            # look for a module
            for loader, suffix in self._loaders:
                src = tree.get((*parts[:-1], parts[-1] + suffix))
                if isinstance(src, str):
                    return build_module_spec(loader, fullname, src, None)

            # namespace
            if namespace:
                spec = importlib.machinery.ModuleSpec(fullname, None)
                spec.submodule_search_locations = []
                return spec

        return None

    @functools.lru_cache(maxsize=1)
    def rebuild(self) -> Node:
        # skip editable wheel lookup during rebuild: during the build
        # the module we are rebuilding might be imported causing a
        # rebuild loop.
        env = os.environ.copy()
        env[MARKER] = os.pathsep.join((env.get(MARKER, ''), self._build_path))

        if self._verbose or bool(env.get(VERBOSE, '')):
            print('+ ' + ' '.join(self._build_cmd))
            stdout = None
        else:
            stdout = subprocess.DEVNULL

        subprocess.run(self._build_cmd, cwd=self._build_path, env=env, stdout=stdout, check=True)

        install_plan_path = os.path.join(self._build_path, 'meson-info', 'intro-install_plan.json')
        with open(install_plan_path, 'r', encoding='utf8') as f:
            install_plan = json.load(f)
        return collect(install_plan)


def install(names: Set[str], path: str, cmd: List[str], verbose: bool) -> None:
    sys.meta_path.insert(0, MesonpyMetaFinder(names, path, cmd, verbose))
