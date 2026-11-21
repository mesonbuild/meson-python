# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('examplelib', 'c', version: '1.0.0')

examplelib = static_library('example', 'src/example.c', install: not meson.is_subproject())
example_dep = declare_dependency(link_with: examplelib, include_directories: 'src')

if not meson.is_subproject()
  install_headers('src/example.h')
endif
