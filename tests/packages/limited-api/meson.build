# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('limited-api', 'c', version: '1.0.0')

py = import('python').find_installation(pure: false)

py.extension_module(
  'module',
  'module.c',
  limited_api: '3.7',
  install: true,
)

if get_option('extra')
  py.extension_module(
    'extra',
    'module.c',
    install: true,
  )
endif
