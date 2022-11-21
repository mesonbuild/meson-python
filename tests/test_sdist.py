# SPDX-License-Identifier: MIT

import os
import stat
import sys
import tarfile
import textwrap

import pytest

import mesonpy

from .conftest import in_git_repo_context


def test_contents(sdist_library):
    with tarfile.open(sdist_library, 'r:gz') as sdist:
        names = set(sdist.getnames())

    assert names == {
        'library-1.0.0/example.c',
        'library-1.0.0/examplelib.c',
        'library-1.0.0/examplelib.h',
        'library-1.0.0/meson.build',
        'library-1.0.0/pyproject.toml',
        'library-1.0.0/PKG-INFO',
    }


def test_contents_subdirs(sdist_subdirs):
    with tarfile.open(sdist_subdirs, 'r:gz') as sdist:
        names = set(sdist.getnames())

    assert names == {
        'subdirs-1.0.0/PKG-INFO',
        'subdirs-1.0.0/meson.build',
        'subdirs-1.0.0/pyproject.toml',
        'subdirs-1.0.0/subdirs/__init__.py',
        'subdirs-1.0.0/subdirs/a/__init__.py',
        'subdirs-1.0.0/subdirs/a/b/c.py',
        'subdirs-1.0.0/subdirs/b/c.py',
    }


def test_contents_unstaged(package_pure, tmp_path):
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

            sdist_path = mesonpy.build_sdist(os.fspath(tmp_path))
    finally:
        with open('pure.py', 'w') as f:
            f.write(old_data)
        os.unlink('crap')

    with tarfile.open(tmp_path / sdist_path, 'r:gz') as sdist:
        names = set(sdist.getnames())
        read_data = sdist.extractfile('pure-1.0.0/pure.py').read().replace(b'\r\n', b'\n')

    assert names == {
        'pure-1.0.0/PKG-INFO',
        'pure-1.0.0/meson.build',
        'pure-1.0.0/pure.py',
        'pure-1.0.0/pyproject.toml',
    }
    assert read_data == new_data.encode()


@pytest.mark.skipif(sys.platform in {'win32', 'cygwin'}, reason='Platform does not support executable bit')
def test_executable_bit(sdist_executable_bit):
    expected = {
        'executable_bit-1.0.0/PKG-INFO': False,
        'executable_bit-1.0.0/example-script.py': True,
        'executable_bit-1.0.0/example.c': False,
        'executable_bit-1.0.0/executable_module.py': True,
        'executable_bit-1.0.0/meson.build': False,
        'executable_bit-1.0.0/pyproject.toml': False,
    }

    with tarfile.open(sdist_executable_bit, 'r:gz') as sdist:
        for member in sdist.getmembers():
            assert bool(member.mode & stat.S_IXUSR) == expected[member.name]


def test_generated_files(sdist_generated_files):
    expected = {
        'executable_bit-1.0.0/PKG-INFO',
        'executable_bit-1.0.0/example-script.py',
        'executable_bit-1.0.0/example.c',
        'executable_bit-1.0.0/executable_module.py',
        'executable_bit-1.0.0/meson.build',
        'executable_bit-1.0.0/pyproject.toml',
        'executable_bit-1.0.0/_version_meson.py',
        'executable_bit-1.0.0/generate_version.py',
    }
    with tarfile.open(sdist_generated_files, 'r:gz') as sdist:
        assert set(tar.name for tar in sdist.getmembers()) == expected
