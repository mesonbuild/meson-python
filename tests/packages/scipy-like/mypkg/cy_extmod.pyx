# SPDX-FileCopyrightText: 2022 meson-python developers
#
# SPDX-License-Identifier: MIT

from libc.math cimport sin


cdef double f(double x):
    return sin(x * x)
