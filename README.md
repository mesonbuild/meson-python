# mesonpy [![PyPI version](https://badge.fury.io/py/meson-python.svg)](https://pypi.org/project/meson-python/)

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/FFY00/mesonpy/main.svg)](https://results.pre-commit.ci/latest/github/FFY00/mesonpy/main)
[![checks](https://github.com/FFY00/mesonpy/actions/workflows/checks.yml/badge.svg)](https://github.com/FFY00/mesonpy/actions/workflows/checks.yml)
[![tests](https://github.com/FFY00/mesonpy/actions/workflows/tests.yml/badge.svg)](https://github.com/FFY00/mesonpy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/FFY00/mesonpy/branch/main/graph/badge.svg?token=xcb2u2YvVk)](https://codecov.io/gh/FFY00/mesonpy)

Python build backend ([PEP 517](https://www.python.org/dev/peps/pep-0517/)) for Meson projects.

### Usage

#### Enabling the build backend

To use this build backend, you must specify it in your `pyproject.toml` file.

```toml
[build-system]
build-backend = 'mesonpy'
requires = [
  'meson-python',
]
```

If you have any other build dependencies, you must also add them to the
`requires` list.

#### Specifying the project metadata

`mesonpy` supports specifying Python package metadata in the `project` table in
`pyproject.toml` ([PEP 621](https://www.python.org/dev/peps/pep-0621/)).

To do so, you just need to add a `project` section with the details you want to
specify (see [PEP 621](https://www.python.org/dev/peps/pep-0621/) for the
specification of the format).

```toml
...

[project]
name = 'orion'
version = '1.2.3'
description = 'The Orion constellation!'
readme = 'README.md'
license = { file = 'LICENSE' }
keyword = ['constellation', 'stars', 'sky']
authors = [
  { name = 'Filipe Laíns', email = 'lains@riseup.net' },
]
classifiers = [
  'Development Status :: 4 - Beta',
  'Programming Language :: Python',
]

requires-python = '>=3.7'
dependencies = [
  'stars >= 1.0.0',
  'location < 3',
]

[project.optional-dependencies]
test = [
  'pytest >= 3',
  'telescope',
]

[project.urls]
homepage = 'https://constellations.example.com/orion'
repository = 'https://constellations.example.com/orion/repo'
documentation = 'https://constellations.example.com/orion/docs'
changelog = 'https://constellations.example.com/orion/docs/changelog.html'
```

In case you want `mesonpy` to detect the version automatically from Meson, you
can omit the `version` field and add it to `project.dynamic`.

```toml
[project]
name = 'orion'
dynamic = [
  'version',
]
...
```

#### Automatic metadata

If no other metadata is specified, `mesonpy` will fetch the project name and
version from Meson. In which case, you don't need to add anything else to your
`pyproject.toml` file.

This is not recommended. Please consider specifying the Python package metadata.

### Status

- Pure Python modules :+1:
- Native modules
  - Don't link against anything :+1:
  - Link aginst external libraries :+1:
  - Link aginst libraries from the Meson project :+1:
  - Detect the ABI :+1:
- Scripts (executables in Meson)
  - Don't link aginst anything :+1:
  - Link against external libraries :+1:
  - Link against libraries from the Meson project :hammer:

#### Platform Support

- Linux :+1:
- Windows :soon:
- MacOS :soon:
- Other UNIX-like :warning:
  - Most platforms should work, but currently that is not tested or guaranteed

### Limitations

#### No data

Data ([`install_data`](https://mesonbuild.com/Reference-manual_functions.html#install_data))
is not supported by the wheel standard. Project should install data as Python
source instead (Python source does not have to be only Python files!) and use
[`importlib.resources`](https://docs.python.org/3/library/importlib.html#module-importlib.resources)
(or the [`importlib_resources`](https://github.com/python/importlib_resources)
backport) to access the data. If you really need the data to be installed where
it was previously (eg. `/usr/data`), you can do so at runtime.
