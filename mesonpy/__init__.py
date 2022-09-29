# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2021 Quansight, LLC
# SPDX-FileCopyrightText: 2021 Filipe Laíns <lains@riseup.net>


"""Meson Python build backend

Implements PEP 517 hooks.
"""

from __future__ import annotations

import collections
import contextlib
import functools
import io
import itertools
import json
import os
import pathlib
import platform
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
    import pyproject_metadata  # noqa: F401
    import wheel.wheelfile  # noqa: F401


if sys.version_info >= (3, 8):
    from functools import cached_property
else:
    cached_property = lambda x: property(functools.lru_cache(maxsize=None)(x))  # noqa: E731


__version__ = '0.9.0'


class _depstr:
    """Namespace that holds the requirement strings for dependencies we *might*
    need at runtime. Having them in one place makes it easier to update.
    """
    patchelf = 'patchelf >= 0.11.0'
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
    """Callable to override the default warning handler, to have colored output."""
    print('{yellow}WARNING{reset} {}'.format(message, **_STYLES))


def _setup_cli() -> None:
    """Setup CLI stuff (eg. handlers, hooks, etc.). Should only be called when
    actually we are in control of the CLI, not on a normal import.
    """
    warnings.showwarning = _showwarning

    try:  # pragma: no cover
        import colorama
    except ModuleNotFoundError:  # pragma: no cover
        pass
    else:  # pragma: no cover
        colorama.init()  # fix colors on windows


class MesonBuilderError(Exception):
    """Error when building the Meson package."""


class _WheelBuilder():
    """Helper class to build wheels from projects."""

    # Maps wheel scheme names to Meson placeholder directories
    _SCHEME_MAP: ClassVar[Dict[str, Tuple[str, ...]]] = {
        'scripts': ('{bindir}',),
        'purelib': ('{py_purelib}',),
        'platlib': ('{py_platlib}', '{moduledir_shared}'),
        'headers': ('{includedir}',),
        'data': ('{datadir}',),
        # our custom location
        'mesonpy-libs': ('{libdir}', '{libdir_shared}')
    }

    def __init__(
        self,
        project: Project,
        source_dir: pathlib.Path,
        install_dir: pathlib.Path,
        build_dir: pathlib.Path,
        sources: Dict[str, Dict[str, Any]],
        copy_files: Dict[str, str],
    ) -> None:
        self._project = project
        self._source_dir = source_dir
        self._install_dir = install_dir
        self._build_dir = build_dir
        self._sources = sources
        self._copy_files = copy_files

        self._libs_build_dir = self._build_dir / 'mesonpy-wheel-libs'

    @cached_property
    def _wheel_files(self) -> DefaultDict[str, List[Tuple[pathlib.Path, str]]]:
        return self._map_to_wheel(self._sources, self._copy_files)

    @property
    def _has_internal_libs(self) -> bool:
        return bool(self._wheel_files['mesonpy-libs'])

    @property
    def basename(self) -> str:
        """Normalized wheel name and version (eg. meson_python-1.0.0)."""
        return '{distribution}-{version}'.format(
            distribution=self._project.name.replace('-', '_'),
            version=self._project.version,
        )

    @property
    def name(self) -> str:
        """Wheel name, this includes the basename and tags."""
        return '{basename}-{python_tag}-{abi_tag}-{platform_tag}'.format(
            basename=self.basename,
            python_tag=self.python_tag,
            abi_tag=self.abi_tag,
            platform_tag=self.platform_tag,
        )

    @property
    def distinfo_dir(self) -> str:
        return f'{self.basename}.dist-info'

    @property
    def data_dir(self) -> str:
        return f'{self.basename}.data'

    @cached_property
    def is_pure(self) -> bool:
        """Is the wheel "pure" (architecture independent)?"""
        # XXX: I imagine some users might want to force the package to be
        # non-pure, but I think it's better that we evaluate use-cases as they
        # arise and make sure allowing the user to override this is indeed the
        # best option for the use-case.
        if self._wheel_files['platlib']:
            return False
        for _, file in self._wheel_files['scripts']:
            if self._is_native(file):
                return False
        return True

    @property
    def wheel(self) -> bytes:  # noqa: F811
        """Return WHEEL file for dist-info."""
        return textwrap.dedent('''
            Wheel-Version: 1.0
            Generator: meson
            Root-Is-Purelib: {is_purelib}
            Tag: {tags}
        ''').strip().format(
            is_purelib='true' if self.is_pure else 'false',
            tags=f'{self.python_tag}-{self.abi_tag}-{self.platform_tag}',
        ).encode()

    @property
    def _debian_python(self) -> bool:
        """Check if we are running on Debian-patched Python."""
        try:
            import distutils
            try:
                import distutils.command.install
            except ModuleNotFoundError:
                raise ModuleNotFoundError('Unable to import distutils, please install python3-distutils')
            return 'deb_system' in distutils.command.install.INSTALL_SCHEMES
        except ModuleNotFoundError:
            return False

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

    @cached_property
    def platform_tag(self) -> str:
        if self.is_pure:
            return 'any'
        # XXX: Choose the sysconfig platform here and let something like auditwheel
        #      fix it later if there are system dependencies (eg. replace it with a manylinux tag)
        platform_ = sysconfig.get_platform()
        parts = platform_.split('-')
        if parts[0] == 'macosx':
            target = os.environ.get('MACOSX_DEPLOYMENT_TARGET')
            if target:
                print(
                    '{yellow}MACOSX_DEPLOYMENT_TARGET is set so we are setting the '
                    'platform tag to {target}{reset}'.format(target=target, **_STYLES)
                )
                parts[1] = target
            else:
                # If no target macOS version is specified fallback to
                # platform.mac_ver() instead of sysconfig.get_platform() as the
                # latter specifies the target macOS version Python was built
                # against.
                parts[1] = platform.mac_ver()[0]

            if parts[1] in ('11', '12'):
                # Workaround for bug where pypa/packaging does not consider macOS
                # tags without minor versions valid. Some Python flavors (Homebrew
                # for example) on macOS started to do this in version 11, and
                # pypa/packaging should handle things correctly from version 13 and
                # forward, so we will add a 0 minor version to MacOS 11 and 12.
                # https://github.com/FFY00/meson-python/issues/91
                # https://github.com/pypa/packaging/issues/578
                parts[1] += '.0'

            platform_ = '-'.join(parts)
        elif parts[0] == 'linux' and parts[1] == 'x86_64' and sys.maxsize == 0x7fffffff:
            # 32-bit Python running on an x86_64 host
            # https://github.com/FFY00/meson-python/issues/123
            parts[1] = 'i686'
            platform_ = '-'.join(parts)
        return platform_.replace('-', '_').replace('.', '_')

    def _calculate_file_abi_tag_heuristic_windows(self, filename: str) -> Optional[mesonpy._tags.Tag]:
        """Try to calculate the Windows tag from the Python extension file name."""
        match = _WINDOWS_NATIVE_MODULE_REGEX.match(filename)
        if not match:
            return None
        tag = match.group('tag')

        try:
            return mesonpy._tags.StableABITag(tag)
        except ValueError:
            return mesonpy._tags.InterpreterTag(tag)

    def _calculate_file_abi_tag_heuristic_posix(self, filename: str) -> Optional[mesonpy._tags.Tag]:
        """Try to calculate the Posix tag from the Python extension file name."""
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
            return mesonpy._tags.InterpreterTag(tag)

    def _calculate_file_abi_tag_heuristic(self, filename: str) -> Optional[mesonpy._tags.Tag]:
        """Try to calculate the ABI tag from the Python extension file name."""
        if os.name == 'nt':
            return self._calculate_file_abi_tag_heuristic_windows(filename)
        # everything else *should* follow the POSIX way, at least to my knowledge
        return self._calculate_file_abi_tag_heuristic_posix(filename)

    def _file_list_repr(self, files: Collection[str], prefix: str = '\t\t', max_count: int = 3) -> str:
        if len(files) > max_count:
            files = list(itertools.islice(files, max_count)) + [f'(... +{len(files)}))']
        return ''.join(f'{prefix}- {file}\n' for file in files)

    def _files_by_tag(self) -> Mapping[mesonpy._tags.Tag, Collection[str]]:
        """Map files into ABI tags."""
        files_by_tag: Dict[mesonpy._tags.Tag, List[str]] = collections.defaultdict(list)

        for _, file in self._wheel_files['platlib']:
            # if in platlib, calculate the ABI tag
            tag = self._calculate_file_abi_tag_heuristic(file)
            if tag:
                files_by_tag[tag].append(file)

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
            # no selected tag yet, let's assign this one
            if not selected_tag:
                selected_tag = tag
            # interpreter tag
            elif isinstance(tag, mesonpy._tags.InterpreterTag):
                if tag != selected_tag:
                    if isinstance(selected_tag, mesonpy._tags.InterpreterTag):
                        raise ValueError(
                            'Found files with incompatible ABI tags:\n'
                            + self._file_list_repr(tags[selected_tag])
                            + '\tand\n'
                            + self._file_list_repr(files)
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

    def _is_native(self, file: Union[str, pathlib.Path]) -> bool:
        """Check if file is a native file."""
        self._project.build()  # the project needs to be built for this :/

        with open(file, 'rb') as f:
            if platform.system() == 'Linux':
                return f.read(4) == b'\x7fELF'  # ELF
            elif platform.system() == 'Darwin':
                return f.read(4) in (
                    b'\xfe\xed\xfa\xce',  # 32-bit
                    b'\xfe\xed\xfa\xcf',  # 64-bit
                    b'\xcf\xfa\xed\xfe',  # arm64
                    b'\xca\xfe\xba\xbe',  # universal / fat (same as java class so beware!)
                )
            elif platform.system() == 'Windows':
                return f.read(2) == b'MZ'

        # For unknown platforms, check for file extensions.
        _, ext = os.path.splitext(file)
        if ext in ('.so', '.a', '.out', '.exe', '.dll', '.dylib', '.pyd'):
            return True
        return False

    def _warn_unsure_platlib(self, origin: pathlib.Path, destination: pathlib.Path) -> None:
        """Warn if we are unsure if the file should be mapped to purelib or platlib.

        This happens when we use heuristics to try to map a file purelib or
        platlib but can't differentiate between the two. In which case, we place
        the file in platlib to be safe and warn the user.

        If we can detect the file is architecture dependent and indeed does not
        belong in purelib, we will skip the warning.
        """
        # {moduledir_shared} is currently handled in heuristics due to a Meson bug,
        # but we know that files that go there are supposed to go to platlib.
        if self._is_native(origin):
            # The file is architecture dependent and does not belong in puredir,
            # so the warning is skipped.
            return
        warnings.warn(
            'Could not tell if file was meant for purelib or platlib, '
            f'so it was mapped to platlib: {origin} ({destination})',
            stacklevel=2,
        )

    def _map_from_heuristics(self, origin: pathlib.Path, destination: pathlib.Path) -> Optional[Tuple[str, pathlib.Path]]:
        """Extracts scheme and relative destination with heuristics based on the
        origin file and the Meson destination path.
        """
        warnings.warn('Using heuristics to map files to wheel, this may result in incorrect locations')
        sys_vars = sysconfig.get_config_vars().copy()
        sys_vars['base'] = sys_vars['platbase'] = sys.base_prefix
        sys_paths = sysconfig.get_paths(vars=sys_vars)
        # Try to map to Debian dist-packages
        if self._debian_python:
            search_path = origin
            while search_path != search_path.parent:
                search_path = search_path.parent
                if search_path.name == 'dist-packages' and search_path.parent.parent.name == 'lib':
                    calculated_path = origin.relative_to(search_path)
                    warnings.warn(f'File matched Debian heuristic ({calculated_path}): {origin} ({destination})')
                    self._warn_unsure_platlib(origin, destination)
                    return 'platlib', calculated_path
        # Try to map to the interpreter purelib or platlib
        for scheme in ('purelib', 'platlib'):
            # try to match the install path on the system to one of the known schemes
            scheme_path = pathlib.Path(sys_paths[scheme]).absolute()
            destdir_scheme_path = self._install_dir / scheme_path.relative_to(scheme_path.anchor)
            try:
                wheel_path = pathlib.Path(origin).relative_to(destdir_scheme_path)
            except ValueError:
                continue
            if sys_paths['purelib'] == sys_paths['platlib']:
                self._warn_unsure_platlib(origin, destination)
            return 'platlib', wheel_path
        return None  # no match was found

    def _map_from_scheme_map(self, destination: str) -> Optional[Tuple[str, pathlib.Path]]:
        """Extracts scheme and relative destination from Meson paths.

            Meson destination path -> (wheel scheme, subpath inside the scheme)
        Eg. {bindir}/foo/bar       -> (scripts, foo/bar)
        """
        for scheme, placeholder in [
            (scheme, placeholder)
            for scheme, placeholders in self._SCHEME_MAP.items()
            for placeholder in placeholders
        ]:  # scheme name, scheme path (see self._SCHEME_MAP)
            if destination.startswith(placeholder):
                relative_destination = pathlib.Path(destination).relative_to(placeholder)
                return scheme, relative_destination
        return None  # no match was found

    def _map_to_wheel(
        self,
        sources: Dict[str, Dict[str, Any]],
        copy_files: Dict[str, str],
    ) -> DefaultDict[str, List[Tuple[pathlib.Path, str]]]:
        """Map files to the wheel, organized by scheme."""
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
                    or self._map_from_heuristics(
                        pathlib.Path(copy_files[file]),
                        pathlib.Path(meson_destination),
                    )
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

    def _install_path(
        self,
        wheel_file: wheel.wheelfile.WheelFile,  # type: ignore[name-defined]
        counter: mesonpy._util.CLICounter,
        origin: Path,
        destination: pathlib.Path,
    ) -> None:
        """"Install" file or directory into the wheel
        and do the necessary processing before doing so.

        Some files might need to be fixed up to set the RPATH to the internal
        library directory on Linux wheels for eg.
        """
        location = os.fspath(destination).replace(os.path.sep, '/')
        counter.update(location)

        # fix file
        if os.path.isdir(origin):
            for root, dirnames, filenames in os.walk(str(origin)):
                # Sort the directory names so that `os.walk` will walk them in a
                # defined order on the next iteration.
                dirnames.sort()
                for name in sorted(filenames):
                    path = os.path.normpath(os.path.join(root, name))
                    if os.path.isfile(path):
                        arcname = os.path.join(destination, os.path.relpath(path, origin).replace(os.path.sep, '/'))
                        wheel_file.write(path, arcname)
        else:
            if self._has_internal_libs and platform.system() == 'Linux':
                # add .mesonpy.libs to the RPATH of ELF files
                if self._is_native(os.fspath(origin)):
                    # copy ELF to our working directory to avoid Meson having to regenerate the file
                    new_origin = self._libs_build_dir / pathlib.Path(origin).relative_to(self._build_dir)
                    os.makedirs(new_origin.parent, exist_ok=True)
                    shutil.copy2(origin, new_origin)
                    origin = new_origin
                    # add our in-wheel libs folder to the RPATH
                    elf = mesonpy._elf.ELF(origin)
                    libdir_path = f'$ORIGIN/{os.path.relpath(f".{self._project.name}.mesonpy.libs", destination.parent)}'
                    if libdir_path not in elf.rpath:
                        elf.rpath = [*elf.rpath, libdir_path]

            wheel_file.write(origin, location)

    def build(self, directory: Path) -> pathlib.Path:
        import wheel.wheelfile

        self._project.build()  # ensure project is built

        wheel_file = pathlib.Path(directory, f'{self.name}.whl')

        with wheel.wheelfile.WheelFile(wheel_file, 'w') as whl:
            # add metadata
            whl.writestr(f'{self.distinfo_dir}/METADATA', self._project.metadata)
            whl.writestr(f'{self.distinfo_dir}/WHEEL', self.wheel)

            # add license (see https://github.com/FFY00/meson-python/issues/88)
            if self._project.license_file:
                whl.write(
                    self._source_dir / self._project.license_file,
                    f'{self.distinfo_dir}/{os.path.basename(self._project.license_file)}',
                )

            print('{light_blue}{bold}Copying files to wheel...{reset}'.format(**_STYLES))
            with mesonpy._util.cli_counter(
                len(list(itertools.chain.from_iterable(self._wheel_files.values()))),
            ) as counter:
                # install root scheme files
                root_scheme = 'purelib' if self.is_pure else 'platlib'
                for destination, origin in self._wheel_files[root_scheme]:
                    self._install_path(whl, counter, origin, destination)

                # install bundled libraries
                for destination, origin in self._wheel_files['mesonpy-libs']:
                    assert platform.system() == 'Linux', 'Bundling libraries in wheel is currently only supported in POSIX!'
                    destination = pathlib.Path(f'.{self._project.name}.mesonpy.libs', destination)
                    self._install_path(whl, counter, origin, destination)

                # install the other schemes
                for scheme in self._SCHEME_MAP:
                    if scheme in (root_scheme, 'mesonpy-libs'):
                        continue
                    for destination, origin in self._wheel_files[scheme]:
                        destination = pathlib.Path(self.data_dir, scheme, destination)
                        self._install_path(whl, counter, origin, destination)

        return wheel_file


class Project():
    """Meson project wrapper to generate Python artifacts."""

    _ALLOWED_DYNAMIC_FIELDS: ClassVar[List[str]] = [
        'version',
    ]
    _metadata: Optional[pyproject_metadata.StandardMetadata]

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
                import pyproject_metadata  # noqa: F811
            except ModuleNotFoundError:  # pragma: no cover
                self._metadata = None
            else:
                self._metadata = pyproject_metadata.StandardMetadata.from_pyproject(self._config, self._source_dir)
        else:
            print(
                '{yellow}{bold}! Using Meson to generate the project metadata '
                '(no `project` section in pyproject.toml){reset}'.format(**_STYLES)
            )
            self._metadata = None

        if self._metadata:
            self._validate_metadata()

        # make sure the build dir exists
        self._build_dir.mkdir(exist_ok=True)
        self._install_dir.mkdir(exist_ok=True)

        # write the native file
        native_file_data = textwrap.dedent(f'''
            [binaries]
            python = '{sys.executable}'
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

        # set version if dynamic (this fetches it from Meson)
        if self._metadata and 'version' in self._metadata.dynamic:
            self._metadata.version = self.version

    def _proc(self, *args: str) -> None:
        """Invoke a subprocess."""
        print('{cyan}{bold}+ {}{reset}'.format(' '.join(args), **_STYLES))
        subprocess.check_call(list(args))

    def _meson(self, *args: str) -> None:
        """Invoke Meson."""
        with mesonpy._util.cd(self._build_dir):
            return self._proc('meson', *args)

    def _configure(self, reconfigure: bool = False) -> None:
        """Configure Meson project.

        We will try to reconfigure the build directory if possible to avoid
        expensive rebuilds.
        """
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
                # TODO: Allow configuring these arguments
                '-Ddebug=false',
                '-Doptimization=2',
                *setup_args,
            )
        except subprocess.CalledProcessError:
            if reconfigure:  # if failed reconfiguring, try a normal configure
                self._configure()
            else:
                raise

    def _validate_metadata(self) -> None:
        """Check the pyproject.toml metadata and see if there are any issues."""

        assert self._metadata

        # check for unsupported dynamic fields
        unsupported_dynamic = {
            key for key in self._metadata.dynamic
            if key not in self._ALLOWED_DYNAMIC_FIELDS
        }
        if unsupported_dynamic:
            raise MesonBuilderError('Unsupported dynamic fields: {}'.format(
                ', '.join(unsupported_dynamic)),
            )

        # check if we are running on an unsupported interpreter
        if self._metadata.requires_python:
            self._metadata.requires_python.prereleases = True
            if platform.python_version().rstrip('+') not in self._metadata.requires_python:
                raise MesonBuilderError(
                    f'Unsupported Python version `{platform.python_version()}`, '
                    f'expected `{self._metadata.requires_python}`'
                )

    @cached_property
    def _wheel_builder(self) -> _WheelBuilder:
        return _WheelBuilder(
            self,
            self._source_dir,
            self._install_dir,
            self._build_dir,
            self._install_plan,
            self._copy_files,
        )

    @functools.lru_cache(maxsize=None)
    def build(self) -> None:
        """Trigger the Meson build."""
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
        with tempfile.TemporaryDirectory(prefix='.mesonpy-', dir=os.fspath(source_dir)) as tmpdir:
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
        """Meson install_plan metadata."""
        return self._info('intro-install_plan').copy()

    @property
    def _copy_files(self) -> Dict[str, str]:
        """Files that Meson will copy on install and the target location."""
        copy_files = {}
        for origin, destination in self._info('intro-installed').items():
            destination_path = pathlib.Path(destination).absolute()
            copy_files[origin] = os.fspath(
                self._install_dir / destination_path.relative_to(destination_path.anchor)
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
        """Name in meson.build."""
        name = self._info('intro-projectinfo')['descriptive_name']
        assert isinstance(name, str)
        return name

    @property
    def _meson_version(self) -> str:
        """Version in meson.build."""
        name = self._info('intro-projectinfo')['version']
        assert isinstance(name, str)
        return name

    @property
    def name(self) -> str:
        """Project name. Specified in pyproject.toml."""
        name = self._metadata.name if self._metadata else self._meson_name
        assert isinstance(name, str)
        return name.replace('-', '_')

    @property
    def version(self) -> str:
        """Project version. Either specified in pyproject.toml or meson.build."""
        if self._metadata and 'version' not in self._metadata.dynamic:
            version = str(self._metadata.version)
        else:
            version = self._meson_version
        assert isinstance(version, str)
        return version

    @property
    @functools.lru_cache(maxsize=1)
    def metadata(self) -> bytes:  # noqa: C901
        """Project metadata."""
        # the rest of the keys are only available when using PEP 621 metadata
        if not self.pep621:
            return textwrap.dedent(f'''
                Metadata-Version: 2.1
                Name: {self.name}
                Version: {self.version}
            ''').strip().encode()
        # re-import pyproject_metadata to raise ModuleNotFoundError if it is really missing
        import pyproject_metadata  # noqa: F401, F811
        assert self._metadata
        # use self.version as the version may be dynamic -- fetched from Meson
        core_metadata = self._metadata.as_rfc822()
        core_metadata.headers['Version'] = [self.version]
        return bytes(core_metadata)

    @property
    def license_file(self) -> Optional[pathlib.Path]:
        if self._metadata:
            license_ = self._metadata.license
            if license_ and license_.file:
                return pathlib.Path(license_.file)
        return None

    @property
    def is_pure(self) -> bool:
        """Is the wheel "pure" (architecture independent)?"""
        return bool(self._wheel_builder.is_pure)

    @property
    def pep621(self) -> bool:
        """Does the project use PEP 621 metadata?"""
        return self._pep621

    def sdist(self, directory: Path) -> pathlib.Path:
        """Generates a sdist (source distribution) in the specified directory."""
        # generate meson dist file
        self._meson('dist', '--allow-dirty', '--no-tests', '--formats', 'gztar')

        # move meson dist file to output path
        dist_name = f'{self.name}-{self.version}'
        meson_dist_name = f'{self._meson_name}-{self._meson_version}'
        meson_dist_path = pathlib.Path(self._build_dir, 'meson-dist', f'{meson_dist_name}.tar.gz')
        sdist = pathlib.Path(directory, f'{dist_name}.tar.gz')

        with tarfile.open(meson_dist_path, 'r:gz') as meson_dist, mesonpy._util.create_targz(sdist) as (tar, mtime):
            for member in meson_dist.getmembers():
                # skip the generated meson native file
                if member.name == f'{meson_dist_name}/.mesonpy-native-file.ini':
                    continue

                # calculate the file path in the source directory
                assert member.name, member.name
                member_parts = member.name.split('/')
                if len(member_parts) <= 1:
                    continue
                path = self._source_dir.joinpath(*member_parts[1:])

                if not path.is_file():
                    continue

                info = tarfile.TarInfo(member.name)
                file_stat = os.stat(path)
                info.size = file_stat.st_size
                info.mode = int(oct(file_stat.st_mode)[-3:], 8)

                # rewrite the path if necessary, to match the sdist distribution name
                if dist_name != meson_dist_name:
                    info.name = pathlib.Path(
                        dist_name,
                        path.relative_to(self._source_dir)
                    ).as_posix()

                with path.open('rb') as f:
                    tar.addfile(info, fileobj=f)

            # add PKG-INFO to dist file to make it a sdist
            pkginfo_info = tarfile.TarInfo(f'{dist_name}/PKG-INFO')
            if mtime:
                pkginfo_info.mtime = mtime
            pkginfo_info.size = len(self.metadata)  # type: ignore[arg-type]
            tar.addfile(pkginfo_info, fileobj=io.BytesIO(self.metadata))  # type: ignore[arg-type]

        return sdist

    def wheel(self, directory: Path) -> pathlib.Path:  # noqa: F811
        """Generates a wheel (binary distribution) in the specified directory."""
        wheel = self._wheel_builder.build(self._build_dir)

        final_wheel = pathlib.Path(directory, wheel.name)
        shutil.move(os.fspath(wheel), final_wheel)
        return final_wheel


@contextlib.contextmanager
def _project(config_settings: Optional[Dict[Any, Any]]) -> Iterator[Project]:
    """Create the project given the given config settings."""
    if config_settings is None:
        config_settings = {}

    with Project.with_temp_working_dir(
        build_dir=config_settings.get('builddir'),
    ) as project:
        yield project


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
    dependencies = [_depstr.wheel]
    with _project(config_settings) as project:
        if not project.is_pure and platform.system() == 'Linux':
            # we may need patchelf
            if not shutil.which('patchelf'):  # XXX: This is slightly dangerous.
                # patchelf not already acessible on the system
                dependencies.append(_depstr.patchelf)
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
