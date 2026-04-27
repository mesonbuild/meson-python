# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('dist-info-sboms-platlib', version: '1.0.0')

# pure: false exercises the platlib routing path. Projects shipping
# C extensions (pandas, numpy, scipy) all use this; the distinfo
# prefix detection must work for both purelib and platlib roots.
py = import('python').find_installation(pure: false)

distinfo = meson.project_name() + '-' + meson.project_version() + '.dist-info'

install_data('sboms/static.cdx.json',
  install_dir: py.get_install_dir() / distinfo / 'sboms')
