# SPDX-FileCopyrightText: 2023 The meson-python developers
#
# SPDX-License-Identifier: MIT

project('vendored-meson', version: '1.0.0')

py = import('python').find_installation()

if not get_option('custom-meson-used')
    error('Expected option "custom-meson-used" was not specified')
endif
