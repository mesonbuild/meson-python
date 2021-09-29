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


def test_pep621(sdist_full_metadata):
    sdist = tarfile.open(sdist_full_metadata, 'r:gz')

    assert sdist.extractfile('full_metadata-1.2.3/PKG-INFO').read().decode() == textwrap.dedent('''\
        Metadata-Version: 2.1
        Name: full-metadata
        Version: 1.2.3
        Summary: Some package with all of the PEP 621 metadata
        Keywords: full metadata
        Home-page: https://example.com
        Author: Jane Doe
        Author-Email: Unknown <jhon.doe@example.com>
        Maintainer-Email: Jane Doe <jane.doe@example.com>
        Classifier: Development Status :: 4 - Beta
        Classifier: Programming Language :: Python
        Project-URL: Homepage, https://example.com
        Project-URL: Documentation, https://readthedocs.org
        Project-URL: Repository, https://github.com/FFY00/mesonpy
        Project-URL: Changelog, https://github.com/FFY00/mesonpy/blob/master/CHANGELOG.md
        Requires-Python: >=3.10
        Requires-Dist: a
        Requires-Dist: b>1
        Requires-Dist: c>2; os_name != "nt"
        Requires-Dist: d<3; extra == "test"
        Requires-Dist: e[all]; extra == "test"
        Provides-Extra: test
        Description-Content-Type: text/markdown

        # full-metadata

        An example package with all of the PEP 621 metadata!
    ''')
