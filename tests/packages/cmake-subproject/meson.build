# SPDX-FileCopyrightText: 2024 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('cmake-subproject', ['c', 'cpp', 'cython'], version: '1')

if host_machine.system() == 'linux' and meson.version().version_compare('< 1.9.99')
    error('support for CMake subprojects rerquires Meson >= 1.10 on Linux')
endif

if meson.version().version_compare('< 1.3.0')
    dep = import('cmake').subproject('cmaketest').dependency('cmaketest')
else
    dep = dependency('cmaketest')
endif

py = import('python').find_installation()

py.extension_module(
    'cmakesubproject',
    'cmakesubproject.pyx',
    dependencies: dep,
    override_options: ['cython_language=cpp'],
    install: true,
)
