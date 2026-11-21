# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('example', 'c', version: '1.0.0', meson_version: '>=0.64.0')

py = import('python').find_installation()
example_dep = subproject('examplelib').get_variable('example_dep')
py.extension_module('example', 'examplemodule.c', dependencies: example_dep, install: true)
meson.add_dist_script(py, files('prepare_sdist.py'))
