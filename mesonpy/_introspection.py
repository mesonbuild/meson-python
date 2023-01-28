# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
import sysconfig
import typing
import warnings


if typing.TYPE_CHECKING:  # pragma: no cover
    from mesonpy._compat import Mapping


def debian_python() -> bool:
    """Check if we are running on Debian-patched Python."""
    if sys.version_info >= (3, 10):
        return 'deb_system' in sysconfig.get_scheme_names()
    try:
        import distutils
        try:
            import distutils.command.install
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError('Unable to import distutils, please install python3-distutils') from exc
        return 'deb_system' in distutils.command.install.INSTALL_SCHEMES
    except ModuleNotFoundError:
        return False


DEBIAN_PYTHON = debian_python()


def debian_distutils_paths() -> Mapping[str, str]:
    # https://ffy00.github.io/blog/02-python-debian-and-the-install-locations/
    assert sys.version_info < (3, 12) and DEBIAN_PYTHON

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        import distutils.dist

    distribution = distutils.dist.Distribution()
    install_cmd = distribution.get_command_obj('install')
    install_cmd.install_layout = 'deb'  # type: ignore[union-attr]
    install_cmd.finalize_options()  # type: ignore[union-attr]

    return {
        'data': install_cmd.install_data,  # type: ignore[union-attr]
        'platlib': install_cmd.install_platlib,  # type: ignore[union-attr]
        'purelib': install_cmd.install_purelib,  # type: ignore[union-attr]
        'scripts': install_cmd.install_scripts,  # type: ignore[union-attr]
    }


def sysconfig_paths() -> Mapping[str, str]:
    sys_vars = sysconfig.get_config_vars().copy()
    sys_vars['base'] = sys_vars['platbase'] = sys.base_prefix
    if DEBIAN_PYTHON:
        if sys.version_info >= (3, 10, 3):
            return sysconfig.get_paths('deb_system', vars=sys_vars)
        else:
            return debian_distutils_paths()
    return sysconfig.get_paths(vars=sys_vars)


SYSCONFIG_PATHS = sysconfig_paths()


__all__ = [
    'DEBIAN_PYTHON',
    'SYSCONFIG_PATHS',
]
