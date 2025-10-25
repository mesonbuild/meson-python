# SPDX-FileCopyrightText: 2025 The meson-python developers
#
# SPDX-License-Identifier: MIT

import importlib.resources

data = importlib.resources.files(__package__).joinpath('data.txt').read_text()
uuid = importlib.resources.files(__package__).joinpath('uuid.txt').read_text()
