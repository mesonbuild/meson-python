# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>


"""Meson Python build backend

Implements PEP 517 hooks.
"""

from __future__ import annotations

import abc
import collections
import contextlib
import functools
import gzip
import itertools
import json
import os
import os.path
import pathlib
import re
import shutil
import subprocess
import sys
import sysconfig
import tarfile
import tempfile
import textwrap
import typing
import warnings

from typing import (
    IO, Any, ClassVar, DefaultDict, Dict, Iterable, Iterator, List, Optional,
    Set, TextIO, Tuple, Type, Union
)

import tomli


if sys.version_info >= (3, 9):
    from collections.abc import Collection, Mapping, Sequence
else:
    from typing import Collection, Mapping, Sequence


if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


if typing.TYPE_CHECKING:  # pragma: no cover
    import pep621 as _pep621  # noqa: F401


PathLike = Union[str, os.PathLike]


__version__ = '0.1.2'


class _depstr:
    auditwheel = 'auditwheel >= 5.0.0'
    ninja = 'ninja >= 1.10.0'
    pep621 = 'pep621 >= 0.3.0'
    wheel = 'wheel >= 0.36.0'


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


def _init_colors() -> Dict[str, str]:
    if 'NO_COLOR' in os.environ:
        if 'FORCE_COLOR' in os.environ:
            warnings.warn('Both NO_COLOR and FORCE_COLOR environment variables are set, disabling color')
        return _NO_COLORS
    elif 'FORCE_COLOR' in os.environ or sys.stdout.isatty():
        return _COLORS
    return _NO_COLORS


_STYLES = _init_colors()


_LINUX_NATIVE_MODULE_REGEX = re.compile(r'^(?P<name>.+)\.(?P<tag>.+)\.so$')
_WINDOWS_NATIVE_MODULE_REGEX = re.compile(r'^(?P<name>.+)\.(?P<tag>.+)\.pyd$')
_STABLE_ABI_TAG_REGEX = re.compile(r'^abi(?P<abi_number>[0-9]+)$')


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

    try:  # pragma: no cover
        import colorama
    except ModuleNotFoundError:  # pragma: no cover
        pass
    else:  # pragma: no cover
        colorama.init()  # fix colors on windows


# backport og pathlib.Path.is_relative_to
def is_relative_to(path: pathlib.Path, other: Union[pathlib.Path, str]) -> bool:
    try:
        path.relative_to(other)
    except ValueError:
        return False
    return True


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
def _add_ld_path(paths: Iterable[str]) -> Iterator[None]:
    """Context manager helper to add a path to LD_LIBRARY_PATH."""
    old_value = os.environ.get('LD_LIBRARY_PATH')
    old_paths = old_value.split(os.pathsep) if old_value else []
    os.environ['LD_LIBRARY_PATH'] = os.pathsep.join([*paths, *old_paths])
    try:
        yield
    finally:
        if old_value is not None:  # pragma: no cover
            os.environ['LD_LIBRARY_PATH'] = old_value


@contextlib.contextmanager
def _edit_targz(path: PathLike, new_path: PathLike) -> Iterator[pathlib.Path]:
    """Opens a .tar.gz file in the file system for edition.."""
    with tempfile.TemporaryDirectory(prefix='mesonpy-') as tmpdir:
        workdir = pathlib.Path(tmpdir)
        with tarfile.open(path, 'r:gz') as tar:
            tar.extractall(tmpdir)

        yield workdir

        # reproducibility
        source_date_epoch = os.environ.get('SOURCE_DATE_EPOCH')
        mtime = int(source_date_epoch) if source_date_epoch else None

        file = typing.cast(IO[bytes], gzip.GzipFile(
            os.path.join(path, new_path),
            mode='wb',
            mtime=mtime,
        ))
        with contextlib.closing(file), tarfile.TarFile(
            mode='w',
            fileobj=file,
            format=tarfile.PAX_FORMAT,  # changed in 3.8 to GNU
        ) as tar:
            for path in workdir.rglob('*'):
                if path.is_file():
                    tar.add(
                        name=path,
                        arcname=path.relative_to(workdir).as_posix(),
                    )


class _CLICounter:
    def __init__(self, total: int) -> None:
        self._total = total - 1
        self._count = -1
        self._current_line = ''

    def update(self, description: str) -> None:
        self._count += 1
        new_line = f'[{self._count}/{self._total}] {description}'
        if sys.stdout.isatty():
            pad_size = abs(len(self._current_line) - len(new_line))
            print(' ' + new_line + ' ' * pad_size, end='\r', flush=True)
        else:
            print(new_line)
        self._current_line = new_line

    def finish(self) -> None:
        if sys.stdout.isatty():
            print(f'\r{self._current_line}')


@contextlib.contextmanager
def _cli_counter(total: int) -> Iterator[_CLICounter]:
    counter = _CLICounter(total)
    yield counter
    counter.finish()


class MesonBuilderError(Exception):
    pass


class _Tag(abc.ABC):
    @abc.abstractmethod
    def __init__(self, value: str) -> None: ...

    @abc.abstractmethod
    def __str__(self) -> str: ...

    @property
    @abc.abstractmethod
    def python(self) -> Optional[str]:
        """Python tag."""

    @property
    @abc.abstractmethod
    def abi(self) -> str:
        """ABI tag."""


class _StableABITag(_Tag):
    _REGEX = re.compile(r'^abi(?P<abi_number>[0-9]+)$')

    def __init__(self, value: str) -> None:
        match = self._REGEX.match(value)
        if not match:
            raise ValueError(f'Invalid PEP 3149 stable ABI tag, expecting pattern `{self._REGEX.pattern}`')
        self._abi_number = int(match.group('abi_number'))

    @property
    def abi_number(self) -> int:
        return self._abi_number

    def __str__(self) -> str:
        return f'abi{self.abi_number}'

    @property
    def python(self) -> Literal[None]:
        return None

    @property
    def abi(self) -> str:
        return f'abi{self.abi_number}'

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.abi_number == self.abi_number

    def __hash__(self) -> int:
        return hash(str(self))


class _LinuxInterpreterTag(_Tag):
    def __init__(self, value: str) -> None:
        parts = value.split('-')
        if len(parts) < 2:
            raise ValueError(
                'Invalid PEP 3149 interpreter tag, expected at '
                f'least 2 parts but got {len(parts)}'
            )

        self._implementation = parts[0]
        self._interpreter_version = parts[1]
        self._additional_information = parts[2:]

        if self.implementation not in ('cpython', 'pypy', 'pypy3'):
            raise NotImplementedError(
                f'Unknown Python implementation: {self.implementation}. '
                'Please report this to https://github.com/FFY00/mesonpy/issues '
                'and include information about the Python distribution you are using.'
            )

    @property
    def implementation(self) -> str:
        return self._implementation

    @property
    def interpreter_version(self) -> str:
        return self._interpreter_version

    @property
    def additional_information(self) -> Sequence[str]:
        return tuple(self._additional_information)

    def __str__(self) -> str:
        return '-'.join((
            self.implementation,
            self.interpreter_version,
            *self.additional_information,
        ))

    @property
    def python(self) -> str:
        if self.implementation == 'cpython':
            return f'cp{self.interpreter_version}'
        elif self.implementation in ('pypy', 'pypy3'):
            interpreter_version = f'{sys.version_info[0]}{sys.version_info[1]}'
            return f'pp{interpreter_version}'
        raise ValueError(f'Unknown implementation: {self.implementation}')

    @property
    def abi(self) -> str:
        # XXX: This is a bit flimsy and needs custom logic to support each case,
        #      but currently there's no better way to do it.
        if self.implementation == 'cpython':
            return f'cp{self.interpreter_version}'
        elif self.implementation == 'pypy':
            return f'pypy_{self.interpreter_version}'
        elif self.implementation == 'pypy3':
            return f'pypy3_{self.interpreter_version}'
        raise ValueError(f'Unknown implementation: {self.implementation}')

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, self.__class__)
            and other.implementation == self.implementation
            and other.interpreter_version == self.interpreter_version
        )

    def __hash__(self) -> int:
        return hash(str(self))


class _WindowsInterpreterTag(_Tag):
    def __init__(self, value: str) -> None:
        # XXX: This is not actually standardized, so our implementation relies
        #      on observing how the current software behaves!
        self._parts = value.split('-')
        if len(self.parts) != 2:
            warnings.warn(
                'Unexpected native module tag name, the ABI dectection might be broken. '
                'Please report this to https://github.com/FFY00/mesonpy/issues '
                'and include information about the Python distribution you are using.'
            )

    @property
    def parts(self) -> Sequence[str]:
        return tuple(self._parts)

    def __str__(self) -> str:
        return '-'.join(self.parts)

    @property
    def python(self) -> str:
        return self.abi

    @property
    def abi(self) -> str:
        return self._parts[0]

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and other.parts == self.parts

    def __hash__(self) -> int:
        return hash(str(self))


class _WheelBuilder():
    _SCHEME_MAP: ClassVar[Dict[str, Tuple[str, ...]]] = {
        'scripts': ('{bindir}',),
        'purelib': ('{py_purelib}',),
        'platlib': ('{py_platlib}', '{moduledir_shared}'),
        'headers': ('{include}',),
        'data': ('{datadir}',),
    }
    # XXX: libdir - no match in wheel, we optionally bundle them via auditwheel

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

    @property
    def _debian_python(self) -> bool:
        try:
            import distutils
            try:
                import distutils.command.install
            except ModuleNotFoundError:
                raise ModuleNotFoundError('Unable to import distutils, please install python3-distutils')
            return 'deb_system' in distutils.command.install.INSTALL_SCHEMES
        except ModuleNotFoundError:
            return False

    def _is_elf(self, file: str) -> bool:
        with open(file, 'rb') as f:
            return f.read(4) == b'\x7fELF'

    def _warn_unsure_platlib(self, origin: str, destination: pathlib.Path) -> None:
        if self._is_elf(origin):
            return
        warnings.warn(
            'Could not tell if file was meant for purelib or platlib, '
            f'so it was mapped to platlib: {origin} ({destination})',
            stacklevel=2,
        )

    def _map_from_heuristics(self, origin: str, destination: pathlib.Path) -> Optional[Tuple[str, pathlib.Path]]:
        warnings.warn('Using heuristics to map files to wheel, this may result in incorrect locations')
        sys_vars = sysconfig.get_config_vars()
        sys_vars['base'] = sys_vars['platbase'] = sys.base_prefix
        sys_paths = sysconfig.get_paths(vars=sys_vars)
        # Debian dist-packages
        if self._debian_python:
            search_path = destination
            while search_path != search_path.parent:
                search_path = search_path.parent
                if search_path.name == 'dist-packages' and search_path.parent.parent.name == 'lib':
                    calculated_path = destination.relative_to(search_path)
                    warnings.warn(f'File matched Debian heuristic ({calculated_path}): {origin} ({destination})')
                    self._warn_unsure_platlib(origin, destination)
                    return 'platlib', calculated_path
        # purelib or platlib -- go to wheel root
        for scheme in ('purelib', 'platlib'):
            try:
                wheel_path = destination.relative_to(sys_paths[scheme])
            except ValueError:
                continue
            if sys_paths['purelib'] == sys_paths['platlib']:
                self._warn_unsure_platlib(origin, destination)
            return 'platlib', wheel_path
        return None

    def _map_from_scheme_map(self, destination: str) -> Optional[Tuple[str, pathlib.Path]]:
        for scheme, placeholder in [
            (scheme, placeholder)
            for scheme, placeholders in self._SCHEME_MAP.items()
            for placeholder in placeholders
        ]:  # scheme name, scheme path (see self._SCHEME_MAP)
            if destination.startswith(placeholder):
                relative_destination = pathlib.Path(destination).relative_to(placeholder)
                return scheme, relative_destination
        return None

    def _map_to_wheel(
        self,
        sources: Dict[str, Dict[str, Any]],
        copy_files: Dict[str, str],
    ) -> DefaultDict[str, List[Tuple[pathlib.Path, str]]]:
        relative_destination: Optional[pathlib.Path]
        wheel_files = collections.defaultdict(list)
        for files in sources.values():  # entries in intro-install_plan.json
            for file, details in files.items():  # install path -> {destination, tag}
                # try mapping to wheel location
                meson_destination = details['destination']
                install_details = (
                    # using scheme map
                    self._map_from_scheme_map(meson_destination)
                    # using heuristics
                    or self._map_from_heuristics(copy_files[file], pathlib.Path(meson_destination))
                )
                if install_details:
                    scheme, destination = install_details
                    wheel_files[scheme].append((destination, file))
                    continue
                # not found
                warnings.warn(
                    'File could not be mapped to an equivalent wheel directory: '
                    '{} ({})'.format(copy_files[file], meson_destination)
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
            whl.writestr(f'{self.distinfo_dir}/METADATA', self._project.metadata)
            whl.writestr(f'{self.distinfo_dir}/WHEEL', self.wheel)

            wheel_files = self._map_to_wheel(sources, copy_files)

            print('{light_blue}{bold}Copying files to wheel...{reset}'.format(**_STYLES))
            with _cli_counter(
                len(list(itertools.chain.from_iterable(wheel_files.values()))),
            ) as counter:
                # install root scheme files
                root_scheme = 'purelib' if self._project.is_pure else 'platlib'
                for destination, origin in wheel_files[root_scheme]:
                    location = os.fspath(destination).replace(os.path.sep, '/')
                    counter.update(location)
                    whl.write(origin, location)
                # install the other schemes
                for scheme in self._SCHEME_MAP:
                    if root_scheme == scheme:
                        continue
                    for destination, origin in wheel_files[scheme]:
                        wheel_path = pathlib.Path(f'{self.data_dir}/{scheme}') / destination
                        location = os.fspath(wheel_path).replace(os.path.sep, '/')
                        counter.update(location)
                        whl.write(origin, location)

        return wheel_file


class Project():
    """Meson project wrapper to generate Python artifacts."""

    _ALLOWED_DYNAMIC_FIELDS: ClassVar[List[str]] = [
        'version',
    ]
    _metadata: Optional[_pep621.StandardMetadata]

    def __init__(
        self,
        source_dir: PathLike,
        working_dir: PathLike,
        build_dir: Optional[PathLike] = None,
    ) -> None:
        self._source_dir = pathlib.Path(source_dir).absolute()
        self._working_dir = pathlib.Path(working_dir).absolute()
        self._build_dir = pathlib.Path(build_dir).absolute() if build_dir else (self._working_dir / 'build')
        self._install_dir = self._working_dir / 'install'
        self._meson_native_file = self._source_dir / '.mesonpy-native-file.ini'

        # load config -- PEP 621 support is optional
        self._config = tomli.loads(self._source_dir.joinpath('pyproject.toml').read_text())
        self._pep621 = 'project' in self._config
        if self.pep621:
            try:
                import pep621  # noqa: F811
            except ModuleNotFoundError:  # pragma: no cover
                self._metadata = None
            else:
                self._metadata = pep621.StandardMetadata.from_pyproject(self._config, self._source_dir)
        else:
            print(
                '{yellow}{bold}! Using Meson to generate the project metadata '
                '(no `project` section in pyproject.toml){reset}'.format(**_STYLES)
            )
            self._metadata = None

        # check for unsupported dynamic fields
        if self._metadata:
            unsupported_dynamic = {
                key for key in self._metadata.dynamic
                if key not in self._ALLOWED_DYNAMIC_FIELDS
            }
            if unsupported_dynamic:
                raise MesonBuilderError('Unsupported dynamic fields: {}'.format(
                    ', '.join(unsupported_dynamic)),
                )

        # make sure the build dir exists
        self._build_dir.mkdir(exist_ok=True)
        self._install_dir.mkdir(exist_ok=True)

        # write the native file
        native_file_data = textwrap.dedent(f'''
            [binaries]
            python3 = '{sys.executable}'
        ''')
        native_file_mismatch = (
            not self._meson_native_file.exists()
            or self._meson_native_file.read_text() != native_file_data
        )
        if native_file_mismatch:
            try:
                self._meson_native_file.write_text(native_file_data)
            except OSError:
                # if there are permission errors or something else in the source
                # directory, put the native file in the working directory instead
                # (this won't survive multiple calls -- Meson will have to be reconfigured)
                self._meson_native_file = self._working_dir / '.mesonpy-native-file.ini'
                self._meson_native_file.write_text(native_file_data)

        # configure the meson project; reconfigure if the user provided a build directory
        self._configure(reconfigure=bool(build_dir) and not native_file_mismatch)

    def _proc(self, *args: str) -> None:
        print('{cyan}{bold}+ {}{reset}'.format(' '.join(args), **_STYLES))
        subprocess.check_call(list(args))

    def _meson(self, *args: str) -> None:
        with _cd(self._build_dir):
            return self._proc('meson', *args)

    def _configure(self, reconfigure: bool = False) -> None:
        setup_args = [
            f'--prefix={sys.base_prefix}',
            os.fspath(self._source_dir),
            os.fspath(self._build_dir),
        ]
        if reconfigure:
            setup_args.insert(0, '--reconfigure')

        try:
            self._meson(
                'setup',
                f'--native-file={os.fspath(self._meson_native_file)}',
                *setup_args,
            )
        except subprocess.CalledProcessError:
            if reconfigure:  # if failed reconfiguring, try a normal configure
                self._configure()
            else:
                raise

    @functools.lru_cache(maxsize=None)
    def build(self) -> None:
        self._meson('compile')
        self._meson('install', '--destdir', os.fspath(self._install_dir))

    @classmethod
    @contextlib.contextmanager
    def with_temp_working_dir(
        cls,
        source_dir: PathLike = os.path.curdir,
        build_dir: Optional[PathLike] = None,
    ) -> Iterator[Project]:
        """Creates a project instance pointing to a temporary working directory."""
        with tempfile.TemporaryDirectory(prefix='mesonpy-') as tmpdir:
            yield cls(source_dir, tmpdir, build_dir)

    @functools.lru_cache()
    def _info(self, name: str) -> Dict[str, Any]:
        """Read info from meson-info directory."""
        file = self._build_dir.joinpath('meson-info', f'{name}.json')
        return typing.cast(
            Dict[str, str],
            json.loads(file.read_text())
        )

    @property
    def _install_plan(self) -> Dict[str, Dict[str, Dict[str, str]]]:
        return self._info('intro-install_plan').copy()

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
    def _lib_paths(self) -> Set[str]:
        copy_files = self._copy_files
        return {
            os.path.dirname(copy_files[file])
            for files in self._install_plan.values()
            for file, details in files.items()
            if details['destination'].startswith('{libdir_')
        }

    @property
    def _meson_name(self) -> str:
        name = self._info('intro-projectinfo')['descriptive_name']
        assert isinstance(name, str)
        return name

    @property
    def _meson_version(self) -> str:
        name = self._info('intro-projectinfo')['version']
        assert isinstance(name, str)
        return name

    @property
    def name(self) -> str:
        """Project name."""
        name = self._metadata.name if self._metadata else self._meson_name
        assert isinstance(name, str)
        return name.replace('-', '_')

    @property
    def version(self) -> str:
        """Project version."""
        if self._metadata and 'version' not in self._metadata.dynamic:
            version = str(self._metadata.version)
        else:
            version = self._meson_version
        assert isinstance(version, str)
        return version

    @property
    def metadata(self) -> bytes:  # noqa: C901
        """Project metadata."""
        # the rest of the keys are only available when using PEP 621 metadata
        if not self.pep621:
            return textwrap.dedent(f'''
                Metadata-Version: 2.1
                Name: {self.name}
                Version: {self.version}
            ''').strip().encode()
        # re-import pep621 to raise ModuleNotFoundError if it is really missing
        import pep621  # noqa: F401, F811
        assert self._metadata
        # use self.version as the version may be dynamic -- fetched from Meson
        core_metadata = self._metadata.as_rfc822()
        core_metadata.headers['Version'] = [self.version]
        return bytes(core_metadata)

    @property
    def is_pure(self) -> bool:
        # XXX: I imagine some users might want to force the package to be
        # non-pure, but I think it's better that we evaluate use-cases as they
        # arise and make sure allowing the user to override this is indeed the
        # best option for the use-case.
        not_pure = ('{bindir}', '{libdir_shared}', '{libdir_static}', '{py_platlib}', '{moduledir_shared}')
        for data_type, files in self._install_plan.items():
            for entry in files.values():
                if entry['destination'] is None:  # pragma: no cover
                    continue
                if any(key in entry['destination'] for key in not_pure):
                    return False
        return True

    @property
    def pep621(self) -> bool:
        return self._pep621

    @property
    def python_tag(self) -> str:
        selected_tag = self._select_abi_tag()
        if selected_tag and selected_tag.python:
            return selected_tag.python
        return 'py3'

    @property
    def abi_tag(self) -> str:
        selected_tag = self._select_abi_tag()
        if selected_tag:
            return selected_tag.abi
        return 'none'

    @property
    def platform_tag(self) -> str:
        if self.is_pure:
            return 'any'
        # Choose the sysconfig platform here and let auditwheel fix it later if
        # there are system dependencies (eg. replace it with a manylinux tag)
        return sysconfig.get_platform().replace('-', '_').replace('.', '_')

    def _calculate_file_abi_tag_heuristic_windows(self, filename: str) -> Optional[_Tag]:
        match = _WINDOWS_NATIVE_MODULE_REGEX.match(filename)
        if not match:
            return None
        tag = match.group('tag')

        try:
            return _StableABITag(tag)
        except ValueError:
            return _LinuxInterpreterTag(tag)

    def _calculate_file_abi_tag_heuristic_posix(self, filename: str) -> Optional[_Tag]:
        # sysconfig is not guaranted to export SHLIB_SUFFIX but let's be
        # preventive and check its value to make sure it matches our expectations
        try:
            extension = sysconfig.get_config_vars().get('SHLIB_SUFFIX', '.so')
            if extension != '.so':
                raise NotImplementedError(
                    f"We don't currently support the {extension} extension. "
                    'Please report this to https://github.com/FFY00/mesonpy/issues '
                    'and include information about your operating system.'
                )
        except KeyError:
            warnings.warn(
                'sysconfig does not export SHLIB_SUFFIX, so we are unable to '
                'perform the sanity check regarding the extension suffix. '
                'Please report this to https://github.com/FFY00/mesonpy/issues '
                'and include the output of `python -m sysconfig`.'
            )
        match = _LINUX_NATIVE_MODULE_REGEX.match(filename)
        if not match:  # this file does not appear to be a native module
            return None
        tag = match.group('tag')

        try:
            return _StableABITag(tag)
        except ValueError:
            return _LinuxInterpreterTag(tag)

    def _calculate_file_abi_tag_heuristic(self, filename: str) -> Optional[_Tag]:
        if os.name == 'nt':
            return self._calculate_file_abi_tag_heuristic_windows(filename)
        # everything else *should* follow the POSIX way, at least to my knowledge
        return self._calculate_file_abi_tag_heuristic_posix(filename)

    def _file_list_repr(self, files: Collection[str], prefix: str = '\t\t', max_count: int = 3) -> str:
        if len(files) > max_count:
            files = list(itertools.islice(files, max_count)) + [f'(... +{len(files)}))']
        return ''.join(f'{prefix}- {file}\n' for file in files)

    def _files_by_tag(self) -> Mapping[_Tag, Collection[str]]:
        files_by_tag: Dict[_Tag, List[str]] = collections.defaultdict(list)
        for file, details in self._install_plan.get('targets', {}).items():
            destination = pathlib.Path(details['destination'])
            # if in platlib, calculate the ABI tag
            if (
                not is_relative_to(destination, '{py_platlib}')
                and not is_relative_to(destination, '{moduledir_shared}')
            ):
                continue
            tag = self._calculate_file_abi_tag_heuristic(file)
            if tag:
                files_by_tag[tag] += file
        return files_by_tag

    def _select_abi_tag(self) -> Optional[_Tag]:  # noqa: C901
        """Given a list of ABI tags, selects the most specific one.

        Raises an error if there are incompatible tags.
        """
        # Possibilities:
        #   - interpreter specific (cpython/pypy/etc, version)
        #   - stable abi (abiX)
        tags = self._files_by_tag()
        selected_tag = None
        for tag, files in tags.items():
            if __debug__:  # sanity check
                if os.name == 'nt':
                    assert not isinstance(tag, _LinuxInterpreterTag)
                else:
                    assert not isinstance(tag, _WindowsInterpreterTag)
            # no selected tag yet, let's assign this one
            if not selected_tag:
                selected_tag = tag
            # interpreter tags
            elif isinstance(tag, _LinuxInterpreterTag):
                if tag != selected_tag:
                    if isinstance(selected_tag, _LinuxInterpreterTag):
                        raise ValueError(
                            'Found files with incompatible ABI tags:\n'
                            + self._file_list_repr(tags[selected_tag])
                            + '\tand\n'
                            + self._file_list_repr(files)
                        )
                    selected_tag = tag
            elif isinstance(tag, _WindowsInterpreterTag):
                if tag != selected_tag:
                    if isinstance(selected_tag, _WindowsInterpreterTag):
                        warnings.warn(
                            'Found files with different ABI tags but couldn\'t tell '
                            'if they are incompatible:\n'
                            + self._file_list_repr(tags[selected_tag])
                            + '\tand\n'
                            + self._file_list_repr(files)
                            + 'Please report this to https://github.com/FFY00/mesonpy/issues.'
                        )
                    selected_tag = tag
            # stable ABI
            elif isinstance(tag, _StableABITag):
                if isinstance(selected_tag, _StableABITag) and tag != selected_tag:
                    raise ValueError(
                        'Found files with incompatible ABI tags:\n'
                        + self._file_list_repr(tags[selected_tag])
                        + '\tand\n'
                        + self._file_list_repr(files)
                    )
        return selected_tag

    def sdist(self, directory: PathLike) -> pathlib.Path:
        """Generates a sdist (source distribution) in the specified directory."""
        # generate meson dist file
        self._meson('dist', '--no-tests', '--formats', 'gztar')

        # move meson dist file to output path
        dist_name = f'{self.name}-{self.version}'
        meson_dist_name = f'{self._meson_name}-{self._meson_version}'
        meson_dist = pathlib.Path(self._build_dir, 'meson-dist', f'{meson_dist_name}.tar.gz')
        sdist = pathlib.Path(directory, f'{dist_name}.tar.gz')

        with _edit_targz(meson_dist, sdist) as content:
            # rename from meson name to sdist name if necessary
            if dist_name != meson_dist_name:
                shutil.move(str(content / meson_dist_name), str(content / dist_name))

            # remove .mesonpy-native-file.ini if it exists
            native_file = content / meson_dist_name / '.mesonpy-native-file.ini'
            if native_file.exists():
                native_file.unlink()

            # add PKG-INFO to dist file to make it a sdist
            content.joinpath(dist_name, 'PKG-INFO').write_bytes(self.metadata)

        return sdist

    def wheel(self, directory: PathLike, skip_bundling: bool = True) -> pathlib.Path:
        """Generates a wheel (binary distribution) in the specified directory.

        Bundles the external binary dependencies by default, but can be skiped
        via the ``skip_bundling`` parameter. This results in wheels that are
        only garanteed to work on the current system as it may have external
        dependencies.
        This option is useful for users like Python distributions, which want
        the artifacts to link the system libraries, unlike someone who is
        distributing wheels on PyPI.
        """
        wheel = _WheelBuilder(self).build(self._install_plan, self._copy_files, self._build_dir)

        # return the wheel directly if pure or the user wants to skip the lib bundling step
        if self.is_pure or skip_bundling:
            final_wheel = pathlib.Path(directory, wheel.name)
            shutil.move(os.fspath(wheel), final_wheel)
            return final_wheel

        # use auditwheel to select the correct platform tag based on the external dependencies
        auditwheel_out = self._build_dir / 'auditwheel-output'
        with _cd(self._build_dir), _add_ld_path(self._lib_paths):
            self._proc('auditwheel', 'repair', '-w', os.fspath(auditwheel_out), os.fspath(wheel))

        # get built wheel
        out = list(auditwheel_out.glob('*.whl'))
        assert len(out) == 1
        repaired_wheel = out[0]

        # move to the output directory
        final_wheel = pathlib.Path(directory, repaired_wheel.name)
        shutil.move(os.fspath(repaired_wheel), final_wheel)

        return final_wheel


@contextlib.contextmanager
def _project(config_settings: Optional[Dict[Any, Any]]) -> Iterator[Project]:
    if config_settings is None:
        config_settings = {}

    with Project.with_temp_working_dir(
        build_dir=config_settings.get('builddir'),
    ) as project:
        yield project


def get_requires_for_build_sdist(
    config_settings: Optional[Dict[Any, Any]] = None,
) -> List[str]:
    dependencies = []
    with _project(config_settings) as project:
        if project.pep621:
            dependencies.append(_depstr.pep621)
    return dependencies


def build_sdist(
    sdist_directory: str,
    config_settings: Optional[Dict[Any, Any]] = None,
) -> str:
    _setup_cli()

    out = pathlib.Path(sdist_directory)
    with _project(config_settings) as project:
        return project.sdist(out).name


def get_requires_for_build_wheel(
    config_settings: Optional[Dict[str, str]] = None,
) -> List[str]:
    dependencies = [_depstr.wheel, _depstr.ninja]
    with _project(config_settings) as project:
        if not project.is_pure:
            dependencies.append(_depstr.auditwheel)
        if project.pep621:
            dependencies.append(_depstr.pep621)
    return dependencies


def build_wheel(
    wheel_directory: str,
    config_settings: Optional[Dict[Any, Any]] = None,
    metadata_directory: Optional[str] = None,
) -> str:
    _setup_cli()

    out = pathlib.Path(wheel_directory)
    with _project(config_settings) as project:
        return project.wheel(out).name
