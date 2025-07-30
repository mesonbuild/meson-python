# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('sharedlib-in-package', 'c', version: '1.0.0')

py = import('python').find_installation(pure: false)

origin = build_machine.system() == 'darwin' ? '@loader_path' : '$ORIGIN'

subdir('src')
subdir('mypkg')
