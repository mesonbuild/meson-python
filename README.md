# mesonpy

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FFY00/mesonpy/main.svg)](https://results.pre-commit.ci/latest/github/FFY00/mesonpy/main)
[![checks](https://github.com/FFY00/mesonpy/actions/workflows/checks.yml/badge.svg)](https://github.com/FFY00/mesonpy/actions/workflows/checks.yml)
[![tests](https://github.com/FFY00/mesonpy/actions/workflows/tests.yml/badge.svg)](https://github.com/FFY00/mesonpy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/FFY00/mesonpy/branch/main/graph/badge.svg?token=xcb2u2YvVk)](https://codecov.io/gh/FFY00/mesonpy)

Meson PEP 517 Python build backend.

Currently, mesonpy is only compatible with the Meson `master` branch, as we need [af8b55d49b64e72dbefbd40d613b93f56d17b855](https://github.com/mesonbuild/meson/commit/af8b55d49b64e72dbefbd40d613b93f56d17b855).

It works on both pure Python and compiled projects, and has *optional*
[PEP 621](https://www.python.org/dev/peps/pep-0621/) metadata support.

Currently, it cannot deal with Meson targets that use a custom install location,
but support for this is in progress.
