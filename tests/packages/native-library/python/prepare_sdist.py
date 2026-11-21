# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import subprocess

from pathlib import Path


source = Path(os.environ['MESON_SOURCE_ROOT']).parent
target = Path(os.environ['MESON_DIST_ROOT']) / 'subprojects' / 'examplelib'
if target.is_symlink():
    target.unlink()
for name in ('meson.build', 'src/example.c', 'src/example.h'):
    destination = target / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(subprocess.check_output(['git', 'show', f'HEAD:./{name}'], cwd=source))
