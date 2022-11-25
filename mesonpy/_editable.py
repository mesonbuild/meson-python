import functools
import importlib.abc
import subprocess
import sys

from types import ModuleType
from typing import List, Optional, Union


if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence


# This file should be standalone!
# It is copied during the editable hook installation.


class MesonpyFinder(importlib.abc.MetaPathFinder):
    """Custom loader that whose purpose is to detect when the import system is
    trying to load our modules, and trigger a rebuild. After triggering a
    rebuild, we return None in find_spec, letting the normal finders pick up the
    modules.
    """

    def __init__(
        self,
        project_path: str,
        build_path: str,
        import_paths: List[str],
        top_level_modules: List[str],
        rebuild_commands: List[List[str]],
    ) -> None:
        self._project_path = project_path
        self._build_path = build_path
        self._import_paths = import_paths
        self._top_level_modules = top_level_modules
        self._rebuild_commands = rebuild_commands

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._project_path})'

    @functools.lru_cache(maxsize=1)
    def rebuild(self) -> None:
        for command in self._rebuild_commands:
            subprocess.check_output(command, cwd=self._build_path)

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[Union[str, bytes]]],
        target: Optional[ModuleType] = None,
    ) -> None:
        # if it's one of our modules, trigger a rebuild
        if fullname.split('.', maxsplit=1)[0] in self._top_level_modules:
            self.rebuild()
            # prepend the project path to sys.path, so that the normal finder
            # can find our modules
            # we prepend so that our path comes before the current path (if
            # the interpreter is run with -m), see gh-239
            if sys.path[:len(self._import_paths)] != self._import_paths:
                for path in self._import_paths:
                    if path in sys.path:
                        sys.path.remove(path)
                sys.path = self._import_paths + sys.path
        # return none (meaning we "didn't find" the module) and let the normal
        # finders find/import it
        return None

    @classmethod
    def install(
        cls,
        project_path: str,
        build_path: str,
        import_paths: List[str],
        top_level_modules: List[str],
        rebuild_commands: List[List[str]],
    ) -> None:
        finder = cls(project_path, build_path, import_paths, top_level_modules, rebuild_commands)
        if finder not in sys.meta_path:
            # prepend our finder to sys.meta_path, so that it is queried before
            # the normal finders, and can trigger a project rebuild
            sys.meta_path.insert(0, finder)
            # we add the project path to sys.path later, so that we can prepend
            # after the current directory is prepended (when -m is used)
            # see gh-239


# generated hook install below
