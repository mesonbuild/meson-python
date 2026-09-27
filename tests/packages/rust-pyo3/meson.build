# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('rust-pyo3', 'c', 'rust', version: '1.0.0', meson_version: '>= 1.12.0', default_options: ['rust_std=2024'])

py = import('python').find_installation(pure: false)
pkg = import('rust').workspace().package()

py.extension_module(
    'rust_pyo3',
    'src/lib.rs',
    rust_dependency_map : pkg.rust_dependency_map(),
    rust_args: pkg.rust_args(),
    dependencies : pkg.dependencies(),
    install: true,
)
