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
    session.chdir('docs')
    session.run('sphinx-build', '-M', 'html', '.', '_build')

    if session.posargs:
        if 'serve' in session.posargs:
            print('Launching docs at http://localhost:8000/ - use Ctrl-C to quit')
            session.run('python', '-m', 'http.server', '8000', '-d', '_build/html')
        else:
            print('Unsupported argument to docs')


@nox.session(python='3.7')
def mypy(session):
    session.install('mypy==0.981')

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
