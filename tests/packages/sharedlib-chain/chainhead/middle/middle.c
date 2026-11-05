// SPDX-FileCopyrightText: 2026 The meson-python developers
//
// SPDX-License-Identifier: MIT

extern int leaf(void);

int middle(void) {
    return leaf() + 1;
}
