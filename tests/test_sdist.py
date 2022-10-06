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

    expected = {
        'executable_bit-1.0.0/PKG-INFO': None,
        'executable_bit-1.0.0/example-script.py': True,
        'executable_bit-1.0.0/example.c': False,
        'executable_bit-1.0.0/executable_module.py': True,
        'executable_bit-1.0.0/meson.build': False,
        'executable_bit-1.0.0/pyproject.toml': False,
    }
    assert set(tar.name for tar in sdist.getmembers()) == set(expected.keys())

    def has_execbit(mode):
        # Note: File perms are in octal, but Python returns it in int
        # We check multiple modes, because Docker may set group permissions to
        # match owner permissions
        modes_execbit = 0o755, 0o775
        modes_nonexecbit = 0o644, 0o664
        if mode in modes_execbit:
            return True
        elif mode in modes_nonexecbit:
            return False
        else:
            raise RuntimeError(f'Unknown file permissions mode: {mode}')

    for name, mode in set((tar.name, tar.mode) for tar in sdist.getmembers()):
        if 'PKG-INFO' in name:
            # We match the executable bit on everything but PKG-INFO (we create
            # this ourselves)
            continue
        assert has_execbit(mode) == expected[name], f'Wrong mode for {name}: {mode}'
