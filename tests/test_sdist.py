# SPDX-License-Identifier: EUPL-1.2

import tarfile


def test_contents(sdist_library):
    sdist = tarfile.open(sdist_library, 'r:gz')

    assert set(sdist.getnames()) == {
        'library-1.0.0/example.c',
        'library-1.0.0/examplelib.c',
        'library-1.0.0/meson.build',
        'library-1.0.0/pyproject.toml',
        'library-1.0.0/PKG-INFO',
    }
