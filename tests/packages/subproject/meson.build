# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('subproject', version: '1.0.0')

subproject('dep')

py = import('python').find_installation()

py.install_sources('subproject.py')
