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
import itertools
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import textwrap
import typing
import warnings

from typing import (
    Any, ClassVar, DefaultDict, Dict, List, Optional, Set, TextIO, Tuple, Type,
    Union
)

import tomli

import mesonpy._compat
import mesonpy._elf
import mesonpy._tags
import mesonpy._util

from mesonpy._compat import Collection, Iterator, Mapping, Path


if typing.TYPE_CHECKING:  # pragma: no cover
    import pep621 as _pep621  # noqa: F401
    import wheel.wheelfile  # noqa: F401


__version__ = '0.2.0'


class _depstr:
    ninja = 'ninja >= 1.10.0'
    patchelf_wrapper = 'patchelf-wrapper'
    pep621 = 'pep621 >= 0.3.0'
    wheel = 'wheel >= 0.36.0'  # noqa: F811


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


class MesonBuilderError(Exception):
    pass


class _WheelBuilder():
    _SCHEME_MAP: ClassVar[Dict[str, Tuple[str, ...]]] = {
        'scripts': ('{bindir}',),
        'purelib': ('{py_purelib}',),
        # {moduledir_shared} should be listed in platlib here too, but currently
        # there is a Meson bug preventing us from using, so we will have to let
        # that fallback on heuristics.
        # see https://github.com/mesonbuild/meson/pull/9474
        'platlib': ('{py_platlib}',),
        'headers': ('{include}',),
        'data': ('{datadir}',),
        # our custom location
        'mesonpy-libs': ('{libdir}', '{libdir_shared}')
    }

    """Helper class to build wheels from projects."""
    def __init__(self, project: Project) -> None:
        self._project = project
        self._libs_build_dir = project._build_dir / 'mesonpy-wheel-libs'

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
    def wheel(self) -> bytes:  # noqa: F811
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
            # try to match the install path on the system to one of the known schemes
            scheme_path = pathlib.Path(sys_paths[scheme])
            destdir_scheme_path = self._project._install_dir / scheme_path.relative_to(scheme_path.root)
            try:
                wheel_path = pathlib.Path(origin).relative_to(destdir_scheme_path)
            except ValueError:
                continue
            # {moduledir_shared} is currently handled in heuristics due to a Meson bug,
            # but we know that files that go there are supposed to go to platlib
            if sys_paths['purelib'] == sys_paths['platlib'] and not origin.startswith('{moduledir_shared}'):
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

    def _install_file(
        self,
        wheel_file: wheel.wheelfile.WheelFile,  # type: ignore[name-defined]
        counter: mesonpy._util.CLICounter,
        origin: Path,
        destination: pathlib.Path,
    ) -> None:
        location = os.fspath(destination).replace(os.path.sep, '/')
        counter.update(location)

        # fix file
        if os.name == 'posix':
            # add .mesonpy.libs to the RPATH of ELF files
            if self._is_elf(os.fspath(origin)):
                # copy ELF to our working directory to avoid Meson having to regenerate the file
                new_origin = self._libs_build_dir / pathlib.Path(origin).relative_to(self._project._build_dir)
                os.makedirs(new_origin.parent, exist_ok=True)
                shutil.copy2(origin, new_origin)
                origin = new_origin
                # add our in-wheel libs folder to the RPATH
                elf = mesonpy._elf.ELF(origin)
                libdir_path = f'$ORIGIN/{os.path.relpath(f".{self._project.name}.mesonpy.libs", destination.parent)}'
                if libdir_path not in elf.rpath:
                    elf.rpath = [*elf.rpath, libdir_path]

        wheel_file.write(origin, location)

    def build(
        self,
        sources: Dict[str, Dict[str, Any]],
        copy_files: Dict[str, str],
        directory: Path,
    ) -> pathlib.Path:
        import wheel.wheelfile

        self._project.build()  # ensure project is built

        wheel_file = pathlib.Path(directory, f'{self.name}.whl')
        wheel_files = self._map_to_wheel(sources, copy_files)

        with wheel.wheelfile.WheelFile(wheel_file, 'w') as whl:
            # add metadata
            whl.writestr(f'{self.distinfo_dir}/METADATA', self._project.metadata)
            whl.writestr(f'{self.distinfo_dir}/WHEEL', self.wheel)

            print('{light_blue}{bold}Copying files to wheel...{reset}'.format(**_STYLES))
            with mesonpy._util.cli_counter(
                len(list(itertools.chain.from_iterable(wheel_files.values()))),
            ) as counter:
                # install root scheme files
                root_scheme = 'purelib' if self._project.is_pure else 'platlib'
                for destination, origin in wheel_files[root_scheme]:
                    self._install_file(whl, counter, origin, destination)

                # install bundled libraries
                for destination, origin in wheel_files['mesonpy-libs']:
                    assert os.name == 'posix', 'Bundling libraries in wheel is currently only supported in POSIX!'
                    destination = pathlib.Path(f'.{self._project.name}.mesonpy.libs', destination)
                    self._install_file(whl, counter, origin, destination)

                # install the other schemes
                for scheme in self._SCHEME_MAP:
                    if scheme in (root_scheme, 'mesonpy-libs'):
                        continue
                    for destination, origin in wheel_files[scheme]:
                        destination = pathlib.Path(self.data_dir, scheme, destination)
                        self._install_file(whl, counter, origin, destination)

        return wheel_file


class Project():
    """Meson project wrapper to generate Python artifacts."""

    _ALLOWED_DYNAMIC_FIELDS: ClassVar[List[str]] = [
        'version',
    ]
    _metadata: Optional[_pep621.StandardMetadata]

    def __init__(
        self,
        source_dir: Path,
        working_dir: Path,
        build_dir: Optional[Path] = None,
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
        with mesonpy._util.cd(self._build_dir):
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
        source_dir: Path = os.path.curdir,
        build_dir: Optional[Path] = None,
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
        # XXX: Choose the sysconfig platform here and let something like auditwheel
        #      fix it later if there are system dependencies (eg. replace it with a manylinux tag)
        return sysconfig.get_platform().replace('-', '_').replace('.', '_')

    def _calculate_file_abi_tag_heuristic_windows(self, filename: str) -> Optional[mesonpy._tags.Tag]:
        match = _WINDOWS_NATIVE_MODULE_REGEX.match(filename)
        if not match:
            return None
        tag = match.group('tag')

        try:
            return mesonpy._tags.StableABITag(tag)
        except ValueError:
            return mesonpy._tags.WindowsInterpreterTag(tag)

    def _calculate_file_abi_tag_heuristic_posix(self, filename: str) -> Optional[mesonpy._tags.Tag]:
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
            return mesonpy._tags.StableABITag(tag)
        except ValueError:
            return mesonpy._tags.LinuxInterpreterTag(tag)

    def _calculate_file_abi_tag_heuristic(self, filename: str) -> Optional[mesonpy._tags.Tag]:
        if os.name == 'nt':
            return self._calculate_file_abi_tag_heuristic_windows(filename)
        # everything else *should* follow the POSIX way, at least to my knowledge
        return self._calculate_file_abi_tag_heuristic_posix(filename)

    def _file_list_repr(self, files: Collection[str], prefix: str = '\t\t', max_count: int = 3) -> str:
        if len(files) > max_count:
            files = list(itertools.islice(files, max_count)) + [f'(... +{len(files)}))']
        return ''.join(f'{prefix}- {file}\n' for file in files)

    def _files_by_tag(self) -> Mapping[mesonpy._tags.Tag, Collection[str]]:
        files_by_tag: Dict[mesonpy._tags.Tag, List[str]] = collections.defaultdict(list)
        for file, details in self._install_plan.get('targets', {}).items():
            destination = pathlib.Path(details['destination'])
            # if in platlib, calculate the ABI tag
            if (
                not mesonpy._compat.is_relative_to(destination, '{py_platlib}')
                and not mesonpy._compat.is_relative_to(destination, '{moduledir_shared}')
            ):
                continue
            tag = self._calculate_file_abi_tag_heuristic(file)
            if tag:
                files_by_tag[tag] += file
        return files_by_tag

    def _select_abi_tag(self) -> Optional[mesonpy._tags.Tag]:  # noqa: C901
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
                    assert not isinstance(tag, mesonpy._tags.LinuxInterpreterTag)
                else:
                    assert not isinstance(tag, mesonpy._tags.WindowsInterpreterTag)
            # no selected tag yet, let's assign this one
            if not selected_tag:
                selected_tag = tag
            # interpreter tags
            elif isinstance(tag, mesonpy._tags.LinuxInterpreterTag):
                if tag != selected_tag:
                    if isinstance(selected_tag, mesonpy._tags.LinuxInterpreterTag):
                        raise ValueError(
                            'Found files with incompatible ABI tags:\n'
                            + self._file_list_repr(tags[selected_tag])
                            + '\tand\n'
                            + self._file_list_repr(files)
                        )
                    selected_tag = tag
            elif isinstance(tag, mesonpy._tags.WindowsInterpreterTag):
                if tag != selected_tag:
                    if isinstance(selected_tag, mesonpy._tags.WindowsInterpreterTag):
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
            elif isinstance(tag, mesonpy._tags.StableABITag):
                if isinstance(selected_tag, mesonpy._tags.StableABITag) and tag != selected_tag:
                    raise ValueError(
                        'Found files with incompatible ABI tags:\n'
                        + self._file_list_repr(tags[selected_tag])
                        + '\tand\n'
                        + self._file_list_repr(files)
                    )
        return selected_tag

    def sdist(self, directory: Path) -> pathlib.Path:
        """Generates a sdist (source distribution) in the specified directory."""
        # generate meson dist file
        self._meson('dist', '--no-tests', '--formats', 'gztar')

        # move meson dist file to output path
        dist_name = f'{self.name}-{self.version}'
        meson_dist_name = f'{self._meson_name}-{self._meson_version}'
        meson_dist = pathlib.Path(self._build_dir, 'meson-dist', f'{meson_dist_name}.tar.gz')
        sdist = pathlib.Path(directory, f'{dist_name}.tar.gz')

        with mesonpy._util.edit_targz(meson_dist, sdist) as content:
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

    def wheel(self, directory: Path) -> pathlib.Path:  # noqa: F811
        """Generates a wheel (binary distribution) in the specified directory."""
        wheel = _WheelBuilder(self).build(self._install_plan, self._copy_files, self._build_dir)

        final_wheel = pathlib.Path(directory, wheel.name)
        shutil.move(os.fspath(wheel), final_wheel)
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
            dependencies.append(_depstr.patchelf_wrapper)
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
