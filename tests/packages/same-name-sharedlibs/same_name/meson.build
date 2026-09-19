# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

subdir('competing')
subdir('private')

py.install_sources('__init__.py', subdir: 'same_name')

origin = build_machine.system() == 'darwin' ? '@loader_path' : '$ORIGIN'

# Simulate an external library whose runtime path is supplied through linker
# flags (for example, -Wl,-rpath,... in LDFLAGS). Keep that library inside this
# fixture to make the test self-contained. The requested private installation
# path must take precedence over this preserved competing path.
py.extension_module(
    'choice', 'module.c',
    link_with: private,
    link_args: f'-Wl,-rpath,@origin@/competing',
    install: true,
    subdir: 'same_name',
    install_rpath: '$ORIGIN/private',
)
