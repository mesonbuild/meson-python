# SPDX-FileCopyrightText: 2021 The meson-python developers
#
# SPDX-License-Identifier: MIT

import os
import os.path

import nox


nox.options.sessions = ['docs', 'mypy', 'test']
nox.options.reuse_existing_virtualenvs = True


@nox.session()
def docs(session):
    """
    Build the docs. Pass "serve" to serve.
    """

    session.install('.[docs]')
    session.install('sphinx-autobuild')
    session.install('sphinxcontrib-spelling >= 7.0.0')
    session.chdir('docs')

    spelling_args = ('-b', 'spelling')
    sphinx_build_args = ('.', '_build')

    if not session.posargs:
        # run spell-checking
        session.run('sphinx-build', *spelling_args, *sphinx_build_args)
        # run normal build
        session.run('sphinx-build', *sphinx_build_args)
    else:
        if 'serve' in session.posargs:
            session.run('sphinx-autobuild', *sphinx_build_args)
        else:
            print('Unsupported argument to docs')


@nox.session(python='3.7')
def mypy(session):
    session.install('mypy==0.991')

    session.run('mypy', '-p', 'mesonpy')


@nox.session(python=['3.7', '3.8', '3.9', '3.10', '3.11', 'pypy3.8', 'pypy3.9'])
def test(session):
    htmlcov_output = os.path.join(session.virtualenv.location, 'htmlcov')
    xmlcov_output = os.path.join(session.virtualenv.location, f'coverage-{session.python}.xml')

    session.install('.[test]')

    # optional github actions integration
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        session.install('pytest-github-actions-annotate-failures')

    session.run(
        'pytest',
        '--showlocals', '-vv',
        '--cov',
        f'--cov-report=html:{htmlcov_output}',
        f'--cov-report=xml:{xmlcov_output}',
        *session.posargs
    )
