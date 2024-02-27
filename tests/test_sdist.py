# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import pathlib
import re
import stat
import sys
import tarfile
import textwrap

import pytest

import mesonpy

from .conftest import in_git_repo_context


def test_no_pep621(sdist_library):
    with tarfile.open(sdist_library, 'r:gz') as sdist:
        sdist_pkg_info = sdist.extractfile('library-1.0.0/PKG-INFO').read().decode()

    assert sdist_pkg_info == textwrap.dedent('''\
        Metadata-Version: 2.1
        Name: library
        Version: 1.0.0
    ''')


def test_pep621(sdist_full_metadata):
    with tarfile.open(sdist_full_metadata, 'r:gz') as sdist:
        sdist_pkg_info = sdist.extractfile('full_metadata-1.2.3/PKG-INFO').read().decode()

    metadata = re.escape(textwrap.dedent('''\
        Metadata-Version: 2.1
        Name: full-metadata
        Version: 1.2.3
        Summary: Some package with all of the PEP 621 metadata
        Keywords: full metadata
        Home-page: https://example.com
        Author: Jane Doe
        Author-Email: Unknown <jhon.doe@example.com>
        Maintainer-Email: Jane Doe <jane.doe@example.com>
        License: some license
        Classifier: Development Status :: 4 - Beta
        Classifier: Programming Language :: Python
        Project-URL: Homepage, https://example.com
        Project-URL: Documentation, https://readthedocs.org
        Project-URL: Repository, https://github.com/mesonbuild/meson-python
        Project-URL: Changelog, https://github.com/mesonbuild/meson-python/blob/master/CHANGELOG.rst
        Requires-Python: >=3.7
        Requires-Dist: a
        Requires-Dist: b>1
        Requires-Dist: c>2; os_name != "nt"
        Requires-Dist: d<3; extra == "test"
        Requires-Dist: e[all]; extra == "test"
        Provides-Extra: test
        Description-Content-Type: text/markdown

        <!--
        SPDX-FileCopyrightText: 2021 The meson-python developers

        SPDX-License-Identifier: MIT
        -->

        # full-metadata

        An example package with all of the PEP 621 metadata!
    '''))

    # pyproject-metadata 0.8.0 and later uses a comma to separate keywords
    expr = metadata.replace(r'Keywords:\ full\ metadata', r'Keywords:\ full[ ,]metadata')
    assert re.fullmatch(expr, sdist_pkg_info)


def test_dynamic_version(sdist_dynamic_version):
    with tarfile.open(sdist_dynamic_version, 'r:gz') as sdist:
        sdist_pkg_info = sdist.extractfile('dynamic_version-1.0.0/PKG-INFO').read().decode()

    assert sdist_pkg_info == textwrap.dedent('''\
        Metadata-Version: 2.1
        Name: dynamic-version
        Version: 1.0.0
    ''')


def test_contents(sdist_library):
    with tarfile.open(sdist_library, 'r:gz') as sdist:
        names = {member.name for member in sdist.getmembers()}
        mtimes = {member.mtime for member in sdist.getmembers()}

    assert names == {
        'library-1.0.0/example.c',
        'library-1.0.0/examplelib.c',
        'library-1.0.0/examplelib.h',
        'library-1.0.0/meson.build',
        'library-1.0.0/pyproject.toml',
        'library-1.0.0/PKG-INFO',
    }

    # All the archive members have a valid mtime.
    assert 0 not in mtimes


def test_contents_subdirs(sdist_subdirs):
    with tarfile.open(sdist_subdirs, 'r:gz') as sdist:
        names = {member.name for member in sdist.getmembers()}
        mtimes = {member.mtime for member in sdist.getmembers()}

    assert names == {
        'subdirs-1.0.0/PKG-INFO',
        'subdirs-1.0.0/meson.build',
        'subdirs-1.0.0/pyproject.toml',
        'subdirs-1.0.0/subdirs/__init__.py',
        'subdirs-1.0.0/subdirs/a/__init__.py',
        'subdirs-1.0.0/subdirs/a/b/c.py',
        'subdirs-1.0.0/subdirs/b/c.py',
    }

    # All the archive members have a valid mtime.
    assert 0 not in mtimes


def test_contents_unstaged(package_pure, tmp_path):
    new = textwrap.dedent('''
        def bar():
            return 'foo'
    ''').strip()

    old = pathlib.Path('pure.py').read_text()

    with in_git_repo_context():
        try:
            pathlib.Path('pure.py').write_text(new)
            pathlib.Path('other.py').touch()
            sdist_path = mesonpy.build_sdist(os.fspath(tmp_path))
        finally:
            pathlib.Path('pure.py').write_text(old)
            pathlib.Path('other.py').unlink()

    with tarfile.open(tmp_path / sdist_path, 'r:gz') as sdist:
        names = {member.name for member in sdist.getmembers()}
        mtimes = {member.mtime for member in sdist.getmembers()}
        data = sdist.extractfile('pure-1.0.0/pure.py').read().replace(b'\r\n', b'\n')

    # Verify that uncommitted changes are not included in the sdist.
    assert names == {
        'pure-1.0.0/PKG-INFO',
        'pure-1.0.0/meson.build',
        'pure-1.0.0/pure.py',
        'pure-1.0.0/pyproject.toml',
    }
    assert data == old.encode()

    # All the archive members have a valid mtime.
    assert 0 not in mtimes


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
    with tarfile.open(sdist_generated_files, 'r:gz') as sdist:
        names = {member.name for member in sdist.getmembers()}
        mtimes = {member.mtime for member in sdist.getmembers()}

    assert names == {
        'executable_bit-1.0.0/PKG-INFO',
        'executable_bit-1.0.0/example-script.py',
        'executable_bit-1.0.0/example.c',
        'executable_bit-1.0.0/executable_module.py',
        'executable_bit-1.0.0/meson.build',
        'executable_bit-1.0.0/pyproject.toml',
        'executable_bit-1.0.0/_version_meson.py',
        'executable_bit-1.0.0/generate_version.py',
    }

    # All the archive members have a valid mtime.
    assert 0 not in mtimes


def test_long_path(sdist_long_path):
    # See https://github.com/mesonbuild/meson-python/pull/587#pullrequestreview-2020891328
    # and https://github.com/mesonbuild/meson-python/pull/587#issuecomment-2075973593

    with tarfile.open(sdist_long_path, 'r:gz') as sdist:
        names = {member.name for member in sdist.getmembers()}

    assert names == {
        'long_path-1.0.0/PKG-INFO',
        'long_path-1.0.0/meson.build',
        'long_path-1.0.0/pyproject.toml'
    }
