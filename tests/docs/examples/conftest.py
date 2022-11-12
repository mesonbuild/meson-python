import os
import pathlib

from contextlib import AbstractContextManager

import mesonpy


examples_dir = pathlib.Path(__file__).resolve().parents[3] / 'docs' / 'examples'


class chdir(AbstractContextManager):
    """Non thread-safe context manager to change the current working directory."""

    def __init__(self, path):
        self.path = path
        self._old_cwd = []

    def __enter__(self):
        self._old_cwd.append(os.getcwd())
        os.chdir(self.path)

    def __exit__(self, *excinfo):
        os.chdir(self._old_cwd.pop())


def build_project_wheel(package, outdir):
    with chdir(package):
        return outdir / mesonpy.build_wheel(
            outdir,
            {'builddir': 'build'},
        )
