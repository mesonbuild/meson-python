# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>


"""Meson Python build backend

Implements PEP 517 hooks.
"""

from __future__ import annotations

import contextlib
import email.message
import functools
import gzip
import io
import json
import os
import os.path
import pathlib
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import typing
import warnings

from typing import Any, Dict, Iterator, Optional, TextIO, Type, Union


PathLike = Union[str, os.PathLike]


_COLORS = {
    'cyan': '\33[36m',
    'yellow': '\33[93m',
    'bold': '\33[1m',
    'dim': '\33[2m',
    'underline': '\33[4m',
    'reset': '\33[0m',
}
_NO_COLORS = {color: '' for color in _COLORS}


def _init_colors() -> Dict[str, str]:
    if 'NO_COLOR' in os.environ:
        if 'FORCE_COLOR' in os.environ:
            warnings.warn('Both NO_COLOR and FORCE_COLOR environment variables are set, disabling color')
        return _NO_COLORS
    elif 'FORCE_COLOR' in os.environ or sys.stdout.isatty():
        return _COLORS
    return _NO_COLORS


_STYLES = _init_colors()


def _showwarning(
    message: Union[Warning, str],
    category: Type[Warning],
    filename: str,
    lineno: int,
    file: Optional[TextIO] = None,
    line: Optional[str] = None,
) -> None:  # pragma: no cover
    print('{yellow}WARNING{reset} {}'.format(message, **_STYLES))


def _setup_cli() -> None:
    warnings.showwarning = _showwarning

    try:
        import colorama
    except ModuleNotFoundError:
        pass
    else:
        colorama.init()  # fix colors on windows


@contextlib.contextmanager
def _cd(path: PathLike) -> Iterator[None]:
    """Context manager helper to change the current working directory -- cd."""
    old_cwd = os.getcwd()
    os.chdir(os.fspath(path))
    try:
        yield
    finally:
        os.chdir(old_cwd)


@contextlib.contextmanager
def _edit_targz(path: PathLike) -> Iterator[tarfile.TarFile]:
    """Opens a .tar.gz file in memory for edition."""
    memory = io.BytesIO()
    with gzip.open(path) as compressed:
        memory.write(compressed.read())

    memory.seek(0)
    with tarfile.open(fileobj=memory, mode='a') as tar:
        yield tar

    memory.seek(0)
    with gzip.open(path, 'wb') as new_compressed:
        new_compressed.write(memory.read())  # type: ignore


class MesonBuilderError(Exception):
    pass


class Project():
    """Meson project wrapper to generate Python artifacts."""

    def __init__(self, source_dir: PathLike, working_dir: PathLike) -> None:
        self._source_dir = pathlib.Path(source_dir)
        self._working_dir = pathlib.Path(working_dir)
        self._build_dir = self._working_dir / 'build'
        self._install_dir = self._working_dir / 'build'

        # make sure the build dir exists
        self._build_dir.mkdir(exist_ok=True)
        self._install_dir.mkdir(exist_ok=True)

        # configure the project
        self._meson('setup', os.fspath(source_dir), os.fspath(self._build_dir))

    def _meson(self, *args: str) -> None:
        print('{cyan}{bold}+ meson {}{reset}'.format(' '.join(args), **_STYLES))
        with _cd(self._build_dir):
            subprocess.check_call(['meson', *args])

    @functools.lru_cache(maxsize=None)
    def build(self) -> None:
        self._meson('compile')
        self._meson('install', '--destdir', os.fspath(self._install_dir))

    @classmethod
    @contextlib.contextmanager
    def with_temp_working_dir(cls, source_dir: PathLike = os.path.curdir) -> Iterator[Project]:
        """Creates a project instance pointing to a temporary working directory."""
        with tempfile.TemporaryDirectory(prefix='mesonpy-') as tmpdir:
            yield cls(os.path.abspath(source_dir), tmpdir)

    @functools.lru_cache()
    def _info(self, name: str) -> Dict[str, Any]:
        """Read info from meson-info directory."""
        file = self._build_dir.joinpath('meson-info', f'{name}.json')
        return typing.cast(
            Dict[str, str],
            json.loads(file.read_text())
        )

    @property
    def _install_plan(self) -> Dict[str, Dict[str, Dict[str, Optional[str]]]]:
        plan = self._info('intro-install_plan').copy()
        plan.pop('version')
        return plan

    @property
    def name(self) -> str:
        """Project name."""
        name = self._info('intro-projectinfo')['descriptive_name']
        assert isinstance(name, str)
        return name

    @property
    def version(self) -> str:
        """Project version."""
        version = self._info('intro-projectinfo')['version']
        assert isinstance(version, str)
        return version

    @property
    def metadata(self) -> email.message.Message:
        """Project metadata."""
        metadata = email.message.Message()
        metadata['Metadata-Version'] = '2.1'
        metadata['Name'] = self.name
        metadata['Version'] = self.version
        # FIXME: add missing metadata
        return metadata

    @property
    def is_pure(self) -> bool:
        # XXX: I imagine some users might want to force the package to be
        # non-pure, but I think it's better that we evaluate use-cases as they
        # arise and make sure allowing the user to override this is indeed the
        # best option for the use-case.
        not_pure = ('{bindir}', '{libdir_shared}', '{libdir_static}')
        for data_type, files in self._install_plan.items():
            for entry in files.values():
                if entry['destination'] is None:
                    continue
                if any(key in entry['destination'] for key in not_pure):
                    return False
        return True

    @property
    def python_tag(self) -> str:
        # FIXME: allow users to change this
        return 'py3'

    @property
    def abi_tag(self) -> str:
        # FIXME: select an ABI if there are native modules
        return 'none'

    @property
    def platform_tag(self) -> str:
        # Choose the sysconfig platform here and let auditwheel fix it later if
        # there are system dependencies (eg. replace it with a manylinux tag)
        return sysconfig.get_platform().replace('-', '_').replace('.', '_')

    def sdist(self, directory: PathLike) -> pathlib.Path:
        """Generates a sdist (source distribution) in the specified directory."""
        # generate meson dist file
        self._meson('dist', '--no-tests', '--formats', 'gztar')

        # move meson dist file to output path
        dist_name = f'{self.name}-{self.version}'
        dist_filename = f'{dist_name}.tar.gz'
        meson_dist = pathlib.Path(self._build_dir, 'meson-dist', dist_filename)
        sdist = pathlib.Path(directory, dist_filename)
        shutil.move(meson_dist, sdist)

        # add PKG-INFO to dist file to make it a sdist
        metadata = self.metadata.as_bytes()
        with _edit_targz(sdist) as tar:
            info = tarfile.TarInfo(f'{dist_name}/PKG-INFO')
            info.size = len(metadata)
            with io.BytesIO(metadata) as data:
                tar.addfile(info, data)

        return sdist


def build_sdist(
    sdist_directory: str,
    config_settings: Optional[Dict[Any, Any]] = None,
) -> str:
    _setup_cli()

    out = pathlib.Path(sdist_directory)
    with Project.with_temp_working_dir() as project:
        return project.sdist(out).name


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Dict[Any, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    raise NotImplementedError
