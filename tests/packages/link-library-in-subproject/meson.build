# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project(
    'link-library-in-subproject',
    'c',
    version: '1.0.0',
    meson_version: '>=1.2.0',
)

py = import('python').find_installation(pure: false)

bar_proj = subproject('bar')
bar_dep = bar_proj.get_variable('bar_dep')

subdir('foo')
