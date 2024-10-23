# SPDX-FileCopyrightText: 2022 The meson-python developers
#
# SPDX-License-Identifier: MIT

import datetime
import os
import time
import sys

_build_time = int(os.environ.get('SOURCE_DATE_EPOCH', time.time()))
_build_date = datetime.datetime.fromtimestamp(_build_time, tz=datetime.timezone.utc)

project = 'meson-python'
copyright = f'2021\N{EN DASH}{_build_date.year} The meson-python developers'

html_theme = 'furo'
html_title = f'meson-python'

extensions = [
    'sphinx_copybutton',
    'sphinx_design',
    'sphinxext.opengraph',
    'sphinx.ext.intersphinx',
]

# sphinx.ext.intersphinx
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# sphinxext.opengraph
ogp_site_url = 'https://mesonbuild.com/meson-python/'
ogp_site_name = 'meson-python documentation'
