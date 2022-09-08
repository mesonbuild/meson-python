# SPDX-License-Identifier: MIT

import os
import tarfile
import textwrap

import pytest

import mesonpy

from .conftest import in_git_repo_context


def test_contents(sdist_library):
    sdist = tarfile.open(sdist_library, 'r:gz')

    assert set(sdist.getnames()) == {
        'library-1.0.0/example.c',
        'library-1.0.0/examplelib.c',
        'library-1.0.0/examplelib.h',
        'library-1.0.0/meson.build',
        'library-1.0.0/pyproject.toml',
        'library-1.0.0/PKG-INFO',
    }


def test_contents_subdirs(sdist_subdirs):
    sdist = tarfile.open(sdist_subdirs, 'r:gz')

    assert set(sdist.getnames()) == {
        'subdirs-1.0.0/PKG-INFO',
        'subdirs-1.0.0/meson.build',
        'subdirs-1.0.0/pyproject.toml',
        'subdirs-1.0.0/subdirs/__init__.py',
        'subdirs-1.0.0/subdirs/a/__init__.py',
        'subdirs-1.0.0/subdirs/a/b/c.py',
        'subdirs-1.0.0/subdirs/b/c.py',
    }


def test_contents_unstaged(package_pure, tmpdir):
    new_data = textwrap.dedent('''
    def bar():
        return 'foo'
    ''').strip()

    with open('pure.py', 'r') as f:
        old_data = f.read()

    try:
        with in_git_repo_context():
            with open('pure.py', 'w') as f, open('crap', 'x'):
                f.write(new_data)

            sdist_path = mesonpy.build_sdist(os.fspath(tmpdir))
    finally:
        with open('pure.py', 'w') as f:
            f.write(old_data)
        os.unlink('crap')

    sdist = tarfile.open(tmpdir / sdist_path, 'r:gz')

    assert set(sdist.getnames()) == {
        'pure-1.0.0/PKG-INFO',
        'pure-1.0.0/meson.build',
        'pure-1.0.0/pure.py',
        'pure-1.0.0/pyproject.toml',
    }
    read_data = sdist.extractfile('pure-1.0.0/pure.py').read().replace(b'\r\n', b'\n')
    assert read_data == new_data.encode()


@pytest.mark.skipif(os.name == 'nt', reason='Executable bit does not exist on Windows')
def test_executable_bit(sdist_executable_bit):
    sdist = tarfile.open(sdist_executable_bit, 'r:gz')

    assert set((tar.name, tar.mode) for tar in sdist.getmembers()) == {
        ('executable_bit-1.0.0/PKG-INFO', 420),
        # We match the executable bit on everything
        # but PKG-INFO(we create this ourselves)
        # Note: File perms are in octal, but Python returns it in int
        ('executable_bit-1.0.0/example-script.py', int('755', 8)),
        ('executable_bit-1.0.0/example.c', int('644', 8)),
        ('executable_bit-1.0.0/executable_module.py', int('755', 8)),
        ('executable_bit-1.0.0/meson.build', int('644', 8)),
        ('executable_bit-1.0.0/pyproject.toml', int('644', 8)),
    }
