# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>


"""Meson Python build backend

Implements PEP 517 hooks.
"""

from __future__ import annotations

import collections
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
import textwrap
import typing
import warnings

from typing import Any, ClassVar, Dict, Iterator, List, Optional, TextIO, Tuple, Type, Union


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


class _WheelBuilder():
    _SCHEME_MAP: ClassVar[Dict[str, str]] = {
        'scripts': '{bindir}',
        'purelib': '{py_purelib}',
        'platlib': '{py_platlib}',
        'headers': '{include}',
    }
    # XXX: libdir - no match in wheel, we optionally bundle them via auditwheel
    # XXX: data - no match in wheel

    """Helper class to build wheels from projects."""
    def __init__(self, project: Project) -> None:
        self._project = project

    @property
    def basename(self) -> str:
        return '{distribution}-{version}'.format(
            distribution=self._project.name.replace('-', '_'),
            version=self._project.version,
        )

    @property
    def name(self) -> str:
        return '{basename}-{python_tag}-{abi_tag}-{platform_tag}'.format(
            basename=self.basename,
            python_tag=self._project.python_tag,
            abi_tag=self._project.abi_tag,
            platform_tag=self._project.platform_tag,
        )

    @property
    def distinfo_dir(self) -> str:
        return f'{self.basename}.dist-info'

    @property
    def data_dir(self) -> str:
        return f'{self.basename}.data'

    @property
    def wheel(self) -> bytes:
        '''dist-info WHEEL.'''
        return textwrap.dedent('''
            Wheel-Version: 1.0
            Generator: meson
            Root-Is-Purelib: {is_purelib}
            Tag: {tags}
        ''').strip().format(
            is_purelib='true' if self._project.is_pure else 'false',
            tags=f'{self._project.python_tag}-{self._project.abi_tag}-{self._project.platform_tag}',
        ).encode()

    def _map_to_wheel(
        self,
        sources: Dict[str, Dict[str, Any]],
        copy_files: Dict[str, str],
    ) -> Dict[str, List[Tuple[str, str]]]:
        wheel_files = collections.defaultdict(list)
        for files in sources.values():
            for file, details in files.items():
                destination = details['destination']
                for scheme, path in self._SCHEME_MAP.items():
                    if destination.startswith(path):
                        wheel_files[scheme].append((destination, file))
                        break
                else:
                    warnings.warn(
                        'File could not be mapped to an equivalent wheel directory: '
                        '{} ({})'.format(copy_files[file], destination)
                    )
        return wheel_files

    def build(
        self,
        sources: Dict[str, Dict[str, Any]],
        copy_files: Dict[str, str],
        directory: PathLike,
    ) -> pathlib.Path:
        import wheel.wheelfile

        self._project.build()  # ensure project is built

        wheel_file = pathlib.Path(directory, f'{self.name}.whl')

        with wheel.wheelfile.WheelFile(wheel_file, 'w') as whl:
            # add metadata
            whl.writestr(f'{self.distinfo_dir}/METADATA', self._project.metadata.as_bytes())
            whl.writestr(f'{self.distinfo_dir}/WHEEL', self.wheel)

            wheel_files = self._map_to_wheel(sources, copy_files)

            # install root scheme files
            root_scheme = 'purelib' if self._project.is_pure else 'platlib'
            for destination, origin in wheel_files[root_scheme]:
                wheel_path = pathlib.Path(destination).relative_to(self._SCHEME_MAP[root_scheme])
                whl.write(origin, os.fspath(wheel_path).replace(os.path.sep, '/'))
            # install the other schemes
            for scheme, path in self._SCHEME_MAP.items():
                if root_scheme == scheme:
                    continue
                for destination, origin in wheel_files[scheme]:
                    whl.write(origin, destination.replace(path, f'{self.data_dir}/{scheme}'))

        return wheel_file


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
    def _copy_files(self) -> Dict[str, str]:
        copy_files = {}
        for origin, destination in self._info('intro-installed').items():
            destination_path = pathlib.Path(destination)
            copy_files[origin] = os.fspath(
                self._install_dir / destination_path.relative_to(destination_path.root)
            )
        return copy_files

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

    def wheel(self, directory: PathLike) -> pathlib.Path:
        """Generates a wheel (binary distribution) in the specified directory."""
        sources = self._info('intro-install_plan').copy()
        sources_version = sources.pop('version')
        if sources_version != 1:
            raise MesonBuilderError(f'Unknown intro-install_plan.json schema version: {sources_version}')

        wheel = _WheelBuilder(self).build(sources, self._copy_files, directory)
        return pathlib.Path(directory, wheel.name)


def build_sdist(
    sdist_directory: str,
    config_settings: Optional[Dict[Any, Any]] = None,
) -> str:
    _setup_cli()

    out = pathlib.Path(sdist_directory)
    with Project.with_temp_working_dir() as project:
        return project.sdist(out).name


def get_requires_for_build_wheel(
    config_settings: Optional[Dict[str, str]] = None,
) -> List[str]:
    return ['wheel >= 0.36.0']


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Dict[Any, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    _setup_cli()

    out = pathlib.Path(wheel_directory)
    with Project.with_temp_working_dir() as project:
        return project.wheel(out).name
