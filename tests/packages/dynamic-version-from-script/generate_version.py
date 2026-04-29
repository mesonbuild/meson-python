#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 The meson-python developers
#
# SPDX-License-Identifier: MIT

import argparse
import os
import subprocess


try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


def get_version_from_pyproject():
    here = os.path.dirname(os.path.abspath(__file__))
    pyproject_toml = os.path.join(here, 'pyproject.toml')
    with open(pyproject_toml, 'rb') as f:
        return tomllib.load(f)['project']['version']


def get_git_hash():
    here = os.path.dirname(os.path.abspath(__file__))
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=here,
            capture_output=True,
            check=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return 'unknown'
    return result.stdout.strip()


def write_version_file(outfile, version, git_hash):
    if 'MESON_DIST_ROOT' in os.environ:
        outfile = os.path.join(os.environ['MESON_DIST_ROOT'], outfile)
    with open(outfile, 'w') as f:
        f.write(f"__version__ = '{version}'\n")
        f.write(f"__git_hash__ = '{git_hash}'\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', nargs='?')
    args = parser.parse_args()

    version = get_version_from_pyproject()
    if args.outfile is None:
        print(version)
    else:
        write_version_file(args.outfile, version, get_git_hash())


if __name__ == '__main__':
    main()
