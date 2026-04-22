# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

"""Trivial SBOM generator for the dist-info-sboms test package."""

import json
import sys

with open(sys.argv[1], 'w') as f:
    json.dump({
        'bomFormat': 'CycloneDX',
        'specVersion': '1.6',
        'version': 1,
        'components': [],
    }, f)
