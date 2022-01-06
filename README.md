# mesonpy

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FFY00/mesonpy/main.svg)](https://results.pre-commit.ci/latest/github/FFY00/mesonpy/main)
[![checks](https://github.com/FFY00/mesonpy/actions/workflows/checks.yml/badge.svg)](https://github.com/FFY00/mesonpy/actions/workflows/checks.yml)
[![tests](https://github.com/FFY00/mesonpy/actions/workflows/tests.yml/badge.svg)](https://github.com/FFY00/mesonpy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/FFY00/mesonpy/branch/main/graph/badge.svg?token=xcb2u2YvVk)](https://codecov.io/gh/FFY00/mesonpy)

Meson PEP 517 Python build backend.

It works on both pure Python and compiled projects, and has *optional*
[PEP 621](https://www.python.org/dev/peps/pep-0621/) metadata support.

### Status

- Pure Python modules :+1:
- Native modules
  - Don't link aginst anything :+1:
  - Link aginst external libraries :+1:
  - Link aginst libraries from the Meson project :+1:
  - Detect the ABI :+1:
- Scripts (executables in Meson)
  - Don't link aginst anything :+1:
  - Link against external libraries :+1:
  - Link against libraries from the Meson project :hammer:

### Limitations

#### No data

Data ([`install_data`](https://mesonbuild.com/Reference-manual_functions.html#install_data))
is not supported by the wheel standard. Project should install data as Python
source instead (Python source does not have to be only Python files!) and use
[`importlib.resources`](https://docs.python.org/3/library/importlib.html#module-importlib.resources)
(or the [`importlib_resources`](https://github.com/python/importlib_resources)
backport) to access the data. If you really need the data to be installed where
it was previously (eg. `/usr/data`), you can do so at runtime.
