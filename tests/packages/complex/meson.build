# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('complex', 'c', 'cython', version: '1.0.0')

if host_machine.system() == 'windows' and meson.get_compiler('c').get_id() == 'gcc'
  add_project_arguments('-DMS_WIN64', language: ['c', 'cpp'])
endif

py = import('python').find_installation()

install_subdir('complex', install_dir: py.get_install_dir(pure: false))

py.extension_module('test', 'test.pyx', install: true, subdir: 'complex')
