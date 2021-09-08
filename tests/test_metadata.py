# SPDX-License-Identifier: EUPL-1.2

import tarfile
import textwrap


def test_no_pep621(sdist_library):
    sdist = tarfile.open(sdist_library, 'r:gz')

    assert sdist.extractfile('library-1.0.0/PKG-INFO').read().decode() == textwrap.dedent('''
        Metadata-Version: 2.1
        Name: library
        Version: 1.0.0
    ''').strip()
