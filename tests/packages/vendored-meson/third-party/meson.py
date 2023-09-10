# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

import sys

from mesonbuild import mesonmain


if 'setup' in sys.argv:
    sys.argv.append('-Dcustom-meson-used=true')


if __name__ == '__main__':
    sys.exit(mesonmain.main())
