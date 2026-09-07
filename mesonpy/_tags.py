# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import platform
import struct
import sys
import sysconfig
import typing


if typing.TYPE_CHECKING:  # pragma: no cover
    from typing import TypedDict

    class _Abi(TypedDict):
        extension_suffix: str

    class _ImplementationVersion(TypedDict):
        major: int
        minor: int

    class _Implementation(TypedDict):
        name: str
        version: _ImplementationVersion

    class BuildDetails(TypedDict):
        abi: _Abi
        implementation: _Implementation
        platform: str


# https://peps.python.org/pep-0425/#python-tag
INTERPRETERS = {
    'python': 'py',
    'cpython': 'cp',
    'pypy': 'pp',
    'ironpython': 'ip',
    'jython': 'jy',
}


_32_BIT_INTERPRETER = struct.calcsize('P') == 4


def _get_macosx_platform() -> str:
    ver, _, arch = platform.mac_ver()
    major, minor = map(int, ver.split('.')[:2])

    # Python built with older macOS SDK on macOS 11, reports an
    # nonexistent macOS 10.16 version instead of the real version.
    #
    # The packaging module introduced a workaround
    # https://github.com/pypa/packaging/commit/67c4a2820c549070bbfc4bfbf5e2a250075048da
    #
    # This results in packaging versions up to 21.3 generating
    # platform tags like "macosx_10_16_x86_64" and later versions
    # generating "macosx_11_0_x86_64".  Using the latter would be more
    # correct but prevents the resulting wheel from being installed on
    # systems using packaging 21.3 or earlier (pip 22.3 or earlier).
    #
    # Fortunately packaging versions carrying the workaround still
    # accepts "macosx_10_16_x86_64" as a compatible platform tag.  We
    # can therefore ignore the issue and generate the slightly
    # incorrect tag.

    if _32_BIT_INTERPRETER:
        # 32-bit Python running on a 64-bit kernel.
        if arch == 'ppc64':
            arch = 'ppc'
        if arch == 'x86_64':
            arch = 'i386'

    return f'macosx-{major}.{minor}-{arch}'


def _get_ios_platform() -> str:
    ver = platform.ios_ver().release  # type: ignore[attr-defined]
    major, minor = map(int, ver.split('.')[:2])

    # Although _multiarch is an internal implementation detail, it's a core part
    # of how CPython is implemented on iOS; this attribute is also relied upon
    # by `packaging` as part of tag determination.
    multiarch = sys.implementation._multiarch.replace('-', '_')

    return f'ios-{major}.{minor}-{multiarch}'


def introspect_build_details() -> BuildDetails:
    platform = sysconfig.get_platform()
    if platform.startswith('macosx'):
        platform = _get_macosx_platform()
    elif platform.startswith('ios'):
        platform = _get_ios_platform()
    elif _32_BIT_INTERPRETER:
        # 32-bit Python running on a 64-bit kernel.
        if platform == 'linux-x86_64':
            platform = 'linux_i686'
        if platform == 'linux-aarch64':
            platform = 'linux_armv7l'

    return {
        'abi': {
            # PyPy reports a $SOABI that does not agree with $EXT_SUFFIX.
            # Using $EXT_SUFFIX will not break when PyPy will fix this.
            # See https://foss.heptapod.net/pypy/pypy/-/issues/3816 and
            # https://github.com/pypa/packaging/pull/607.
            'extension_suffix': str(sysconfig.get_config_var('EXT_SUFFIX')),
        },
        'implementation': {
            'name': sys.implementation.name,
            'version': {
                'major': sys.version_info.major,
                'minor': sys.version_info.minor,
            },
        },
        'platform': platform,
    }


def get_interpreter_tag(build_details: BuildDetails) -> str:
    name = build_details['implementation']['name']
    _v = build_details['implementation']['version']
    major = _v['major']
    minor = _v['minor']
    name = INTERPRETERS.get(name, name)
    return f'{name}{major}{minor}'


def get_abi_tag(build_details: BuildDetails) -> str:
    # The best solution to obtain the Python ABI is to parse the
    # $SOABI or $EXT_SUFFIX sysconfig variables as defined in PEP-314.

    # PyPy reports a $SOABI that does not agree with $EXT_SUFFIX.
    # Using $EXT_SUFFIX will not break when PyPy will fix this.
    # See https://foss.heptapod.net/pypy/pypy/-/issues/3816 and
    # https://github.com/pypa/packaging/pull/607.
    ext_suffix = build_details['abi']['extension_suffix']
    empty, abi, ext = ext_suffix.split('.')

    # The packaging module initially based his understanding of the
    # $SOABI variable on the inconsistent value reported by PyPy, and
    # did not strip architecture information from it.  Therefore the
    # ABI tag for later Python implementations (all the ones not
    # explicitly handled below) contains architecture information too.
    # Unfortunately, fixing this now would break compatibility.

    if abi.startswith('cpython'):
        abi = 'cp' + abi.split('-')[1]
    elif abi.startswith('cp'):
        abi = abi.split('-')[0]
    elif abi.startswith('pypy'):
        abi = '_'.join(abi.split('-')[:2])
    elif abi.startswith('graalpy'):
        abi = '_'.join(abi.split('-')[:3])

    return abi.replace('.', '_').replace('-', '_')


def _get_macosx_platform_tag(platform: str) -> str:
    name, ver, arch = platform.split('-', 2)
    assert name == 'macosx'

    # Override the architecture with the one provided in the
    # _PYTHON_HOST_PLATFORM environment variable.  This environment
    # variable affects the sysconfig.get_platform() return value and
    # is used to cross-compile python extensions on macOS for a
    # different architecture.  We base the platform tag computation on
    # platform.mac_ver() but respect the content of the environment
    # variable.
    try:
        arch = os.environ.get('_PYTHON_HOST_PLATFORM', '').split('-')[2]
    except IndexError:
        pass

    # Override the macOS version if one is provided via the
    # MACOSX_DEPLOYMENT_TARGET environment variable.
    try:
        parts = os.environ.get('MACOSX_DEPLOYMENT_TARGET', '').split('.')[:2]
        version = tuple(map(int, parts + ['0'] * (2 - len(parts))))
    except ValueError:
        version = tuple(map(int, ver.split('.')[:2]))

    # The minimum macOS ABI version on arm64 is 11.0.  The macOS SDK
    # on arm64 silently bumps any compatibility version specified via
    # the MACOSX_DEPLOYMENT_TARGET environment variable to 11.0.
    # Despite the platform ABI tag being intended to be a minimum
    # compatibility version, pip refuses to install wheels with a
    # platform tag specifying an ABI version lower than 11.0.  Use
    # 11.0 as minimum ABI version on arm64.
    if arch == 'arm64' and version < (11, 0):
        version = (11, 0)

    major, minor = version

    if major >= 11:
        # For macOS releases up to 10.15, the major version number is
        # actually part of the OS name and the minor version is the
        # actual OS release.  Starting with macOS 11, the major
        # version number is the OS release and the minor version is
        # the patch level.  Reset the patch level to zero.
        minor = 0

    return f'macosx_{major}_{minor}_{arch}'


def _get_ios_platform_tag(platform: str) -> str:
    name, version, multiarch = platform.split('-', 2)
    assert name == 'ios'

    # Override the iOS version if one is provided via the
    # IPHONEOS_DEPLOYMENT_TARGET environment variable.
    try:
        parts = os.environ.get('IPHONEOS_DEPLOYMENT_TARGET', '').split('.')[:2]
        major, minor = map(int, parts + ['0'] * (2 - len(parts)))
    except ValueError:
        major, minor = map(int, version.split('.'))

    return f'ios_{major}_{minor}_{multiarch.replace("-", "_")}'


def get_platform_tag(build_details: BuildDetails) -> str:
    platform = build_details['platform']
    if platform.startswith('macosx'):
        return _get_macosx_platform_tag(platform)
    if platform.startswith('ios'):
        return _get_ios_platform_tag(platform)
    return platform.replace('-', '_').replace('.', '_').lower()


class Tag:
    def __init__(self, interpreter: str | None = None, abi: str | None = None, platform: str | None = None,
                 *, build_details: BuildDetails):
        self.interpreter = interpreter or get_interpreter_tag(build_details)
        self.abi = abi or get_abi_tag(build_details)
        self.platform = platform or get_platform_tag(build_details)

    def __str__(self) -> str:
        return f'{self.interpreter}-{self.abi}-{self.platform}'
