# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import sys
import sysconfig
import typing


if typing.TYPE_CHECKING:  # pragma: no cover
    from mesonpy._compat import Mapping


def sysconfig_paths() -> Mapping[str, str]:
    sys_vars = sysconfig.get_config_vars().copy()
    sys_vars['base'] = sys_vars['platbase'] = sys.base_prefix
    return sysconfig.get_paths(vars=sys_vars)


SYSCONFIG_PATHS = sysconfig_paths()


__all__ = [
    'SYSCONFIG_PATHS',
]
