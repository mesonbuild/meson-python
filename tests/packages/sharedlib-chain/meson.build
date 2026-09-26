# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('sharedlib-chain', 'c', version: '1.0.0')

py = import('python').find_installation(pure: false)

# Request RPATH rather than RUNPATH when supported by the linker.
if meson.get_compiler('c').has_link_argument('-Wl,--disable-new-dtags')
    add_project_link_arguments('-Wl,--disable-new-dtags', language: 'c')
endif

subdir('chainhead')
