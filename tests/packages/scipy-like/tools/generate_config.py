# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

import sys

from pathlib import Path


outfile = Path(sys.argv[1])
outfile.write_text('# Some build-time configuration data')
