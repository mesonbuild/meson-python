# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('scipy-like', 'c', 'cython', version: '2.3.4')

# Work around Python bug on mingw-w64, fixed in Python 3.12
# https://github.com/python/cpython/pull/100137
# The same work-around is also included in Meson 1.1.0 and later.
if meson.version().version_compare('< 1.1')
    if host_machine.system() == 'windows' and meson.get_compiler('c').get_id() == 'gcc'
        add_project_arguments('-DMS_WIN64=', language: 'c')
    endif
endif

py = import('python').find_installation()

subdir('mypkg')
