# SPDX-License-Identifier: EUPL-1.2
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>


"""Meson Python build backend

Implements PEP 517 hooks.
"""

from __future__ import annotations

import collections
import contextlib
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

from typing import Any, ClassVar, DefaultDict, Dict, Iterable, Iterator, List, Optional, Set, TextIO, Tuple, Type, Union

import tomli


if typing.TYPE_CHECKING:  # pragma: no cover
    import pep621 as _pep621  # noqa: F401


PathLike = Union[str, os.PathLike]


class _depstr:
    auditwheel = 'auditwheel >= 4.0.0'
    ninja = 'ninja >= 1.10.0'
    pep621 = 'pep621 >= 0.3.0'
    wheel = 'wheel >= 0.36.0'


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

    try:  # pragma: no cover
        import colorama
    except ModuleNotFoundError:  # pragma: no cover
        pass
    else:  # pragma: no cover
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
    _SCHEME_MAP: ClassVar[Dict[str, Tuple[str, ...]]] = {
        'scripts': ('{bindir}',),
        'purelib': ('{py_purelib}',),
        'platlib': ('{py_platlib}', '{moduledir_shared}'),
        'headers': ('{include}',),
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
    ) -> DefaultDict[str, List[Tuple[pathlib.Path, str]]]:
        wheel_files = collections.defaultdict(list)
        for files in sources.values():
            for file, details in files.items():
                destination = details['destination']
                for scheme, path in [
                    (scheme, path)
                    for scheme, paths in self._SCHEME_MAP.items()
                    for path in paths
                ]:
                    if destination.startswith(path):
                        relative_destination = pathlib.Path(destination).relative_to(path)
                        wheel_files[scheme].append((relative_destination, file))
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
            whl.writestr(f'{self.distinfo_dir}/METADATA', self._project.metadata)
            whl.writestr(f'{self.distinfo_dir}/WHEEL', self.wheel)

            wheel_files = self._map_to_wheel(sources, copy_files)

            # install root scheme files
            root_scheme = 'purelib' if self._project.is_pure else 'platlib'
            for destination, origin in wheel_files[root_scheme]:
                whl.write(origin, os.fspath(destination).replace(os.path.sep, '/'))
            # install the other schemes
            for scheme in self._SCHEME_MAP:
                if root_scheme == scheme:
                    continue
                for destination, origin in wheel_files[scheme]:
                    wheel_path = pathlib.Path(f'{self.data_dir}/{scheme}') / destination
                    whl.write(origin, os.fspath(wheel_path).replace(os.path.sep, '/'))

        return wheel_file


class Project():
    """Meson project wrapper to generate Python artifacts."""

    _ALLOWED_DYNAMIC_FIELDS: ClassVar[List[str]] = [
        'version',
    ]
    _metadata: Optional[_pep621.StandardMetadata]

    def __init__(self, source_dir: PathLike, working_dir: PathLike) -> None:
        self._source_dir = pathlib.Path(source_dir)
        self._working_dir = pathlib.Path(working_dir)
        self._build_dir = self._working_dir / 'build'
        self._install_dir = self._working_dir / 'build'

        # load config -- PEP 621 support is optional
        self._config = tomli.loads(self._source_dir.joinpath('pyproject.toml').read_text())
        self._pep621 = 'project' in self._config
        if self.pep621:
            try:
                import pep621  # noqa: F811
            except ModuleNotFoundError:  # pragma: no cover
                raise
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

        # configure the project
        self._meson('setup', os.fspath(source_dir), os.fspath(self._build_dir))

    def _proc(self, *args: str) -> None:
        print('{cyan}{bold}+ {}{reset}'.format(' '.join(args), **_STYLES))
        subprocess.check_call(list(args))

    def _meson(self, *args: str) -> None:
        with _cd(self._build_dir):
            return self._proc('meson', *args)

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
        not_pure = ('{bindir}', '{libdir_shared}', '{libdir_static}')
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
        # FIXME: allow users to change this
        return 'py3'

    @property
    def abi_tag(self) -> str:
        # FIXME: select an ABI if there are native modules
        return 'none'

    @property
    def platform_tag(self) -> str:
        if self.is_pure:
            return 'any'
        # Choose the sysconfig platform here and let auditwheel fix it later if
        # there are system dependencies (eg. replace it with a manylinux tag)
        return sysconfig.get_platform().replace('-', '_').replace('.', '_')

    def sdist(self, directory: PathLike) -> pathlib.Path:
        """Generates a sdist (source distribution) in the specified directory."""
        # generate meson dist file
        self._meson('dist', '--no-tests', '--formats', 'gztar')

        # move meson dist file to output path
        dist_name = f'{self.name}-{self.version}'
        dist_filename = f'{self._meson_name}-{self._meson_version}.tar.gz'
        meson_dist = pathlib.Path(self._build_dir, 'meson-dist', dist_filename)
        sdist = pathlib.Path(directory, dist_filename)
        shutil.move(os.fspath(meson_dist), sdist)

        # add PKG-INFO to dist file to make it a sdist
        metadata = self.metadata
        with _edit_targz(sdist) as tar:
            info = tarfile.TarInfo(f'{dist_name}/PKG-INFO')
            info.size = len(metadata)
            with io.BytesIO(metadata) as data:
                tar.addfile(info, data)

        return sdist

    def wheel(self, directory: PathLike, skip_bundling: bool = False) -> pathlib.Path:
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


def get_requires_for_build_sdist(
    config_settings: Optional[Dict[Any, Any]] = None,
) -> List[str]:
    dependencies = []
    with Project.with_temp_working_dir() as project:
        if project.pep621:
            dependencies.append(_depstr.pep621)
    return dependencies


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
    dependencies = [_depstr.wheel, _depstr.ninja]
    with Project.with_temp_working_dir() as project:
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
    with Project.with_temp_working_dir() as project:
        return project.wheel(out).name
