#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: 2024 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import sys


outdir = os.path.join(sys.argv[1], 'generated')
os.makedirs(outdir, exist_ok=True)

for name in 'one.py', 'two.py':
    with open(os.path.join(outdir, name), 'w'):
        pass
