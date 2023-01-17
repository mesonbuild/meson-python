import functools
import importlib.abc
import os
import subprocess
import sys
import warnings

from types import ModuleType
from typing import List, Mapping, Optional, Union


if sys.version_info >= (3, 9):
    from collections.abc import Sequence
else:
    from typing import Sequence


# This file should be standalone!
# It is copied during the editable hook installation.


_COLORS = {
    'cyan': '\33[36m',
    'yellow': '\33[93m',
    'light_blue': '\33[94m',
    'bold': '\33[1m',
    'dim': '\33[2m',
    'underline': '\33[4m',
    'reset': '\33[0m',
}
_NO_COLORS = {color: '' for color in _COLORS}


def _init_colors() -> Mapping[str, str]:
    """Detect if we should be using colors in the output. We will enable colors
    if running in a TTY, and no environment variable overrides it. Setting the
    NO_COLOR (https://no-color.org/) environment variable force-disables colors,
    and FORCE_COLOR forces color to be used, which is useful for thing like
    Github actions.
    """
    if 'NO_COLOR' in os.environ:
        if 'FORCE_COLOR' in os.environ:
            warnings.warn('Both NO_COLOR and FORCE_COLOR environment variables are set, disabling color')
        return _NO_COLORS
    elif 'FORCE_COLOR' in os.environ or sys.stdout.isatty():
        return _COLORS
    return _NO_COLORS


_STYLES = _init_colors()  # holds the color values, should be _COLORS or _NO_COLORS


class MesonpyFinder(importlib.abc.MetaPathFinder):
    """Custom loader that whose purpose is to detect when the import system is
    trying to load our modules, and trigger a rebuild. After triggering a
    rebuild, we return None in find_spec, letting the normal finders pick up the
    modules.
    """

    def __init__(
        self,
        project_name: str,
        hook_name: str,
        project_path: str,
        build_path: str,
        import_paths: List[str],
        top_level_modules: List[str],
        rebuild_commands: List[List[str]],
        verbose: bool = False,
    ) -> None:
        self._project_name = project_name
        self._hook_name = hook_name
        self._project_path = project_path
        self._build_path = build_path
        self._import_paths = import_paths
        self._top_level_modules = top_level_modules
        self._rebuild_commands = rebuild_commands
        self._verbose = verbose

        for path in (self._project_path, self._build_path):
            if not os.path.isdir(path):
                raise ImportError(
                    f'{path} is not a directory, but it is required to rebuild '
                    f'"{self._project_name}", which is installed in editable '
                    'mode. Please reinstall the project to get it back to '
                    'working condition. If there are any issues uninstalling '
                    'this installation, you can manually remove '
                    f'{self._hook_name} and {os.path.basename(__file__)}, '
                    f'located in {os.path.dirname(__file__)}.'
                )

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._project_path})'

    def _debug(self, msg: str) -> None:
        if self._verbose:
            print(msg.format(**_STYLES))

    def _proc(self, command: List[str]) -> None:
        # skip editable hook installation in subprocesses, as during the build
        # commands the module we are rebuilding might be imported, causing a
        # rebuild loop
        # see https://github.com/mesonbuild/meson-python/pull/87#issuecomment-1342548894
        env = os.environ.copy()
        env['_MESONPY_EDITABLE_SKIP'] = os.pathsep.join((
            env.get('_MESONPY_EDITABLE_SKIP', ''),
            self._project_path,
        ))

        if self._verbose:
            subprocess.check_call(command, cwd=self._build_path, env=env)
        else:
            subprocess.check_output(command, cwd=self._build_path, env=env)

    @functools.lru_cache(maxsize=1)
    def rebuild(self) -> None:
        self._debug(f'{{cyan}}{{bold}}+ rebuilding {self._project_path}{{reset}}')
        for command in self._rebuild_commands:
            self._proc(command)
        self._debug('{cyan}{bold}+ successfully rebuilt{reset}')

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
        project_name: str,
        hook_name: str,
        project_path: str,
        build_path: str,
        import_paths: List[str],
        top_level_modules: List[str],
        rebuild_commands: List[List[str]],
        verbose: bool = False,
    ) -> None:
        if project_path in os.environ.get('_MESONPY_EDITABLE_SKIP', '').split(os.pathsep):
            return
        if os.environ.get('MESONPY_EDITABLE_VERBOSE', ''):
            verbose = True
        # install our finder
        finder = cls(
            project_name,
            hook_name,
            project_path,
            build_path,
            import_paths,
            top_level_modules,
            rebuild_commands,
            verbose,
        )
        if finder not in sys.meta_path:
            # prepend our finder to sys.meta_path, so that it is queried before
            # the normal finders, and can trigger a project rebuild
            sys.meta_path.insert(0, finder)
            # we add the project path to sys.path later, so that we can prepend
            # after the current directory is prepended (when -m is used)
            # see gh-239


# generated hook install below
