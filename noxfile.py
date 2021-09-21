# SPDX-License-Identifier: MIT

import glob
import os
import os.path

import nox


nox.options.sessions = ['mypy', 'test']
nox.options.reuse_existing_virtualenvs = True


@nox.session(python='3.7')
def mypy(session):
    session.install('mypy')

    session.run('mypy', '-p', 'mesonpy')


@nox.session(python=['3.7', '3.8', '3.9', '3.10'])
def test(session):
    htmlcov_output = os.path.join(session.virtualenv.location, 'htmlcov')
    xmlcov_output = os.path.join(session.virtualenv.location, f'coverage-{session.python}.xml')

    # install from locally built wheel
    session.install('build', 'git+https://github.com/mesonbuild/meson.git', 'ninja', 'packaging', 'tomli', 'pep621')
    session.run('python', '-m', 'build', '-nw', '-o', '.nox-dist')
    session.install(glob.glob('.nox-dist/mesonpy-*.whl')[0])
    # install test extras manually
    session.install('pytest', 'pytest-cov', 'pytest-mock', 'GitPython', 'auditwheel', 'pep621 >= 0.2.0')

    # session.install('.[test]')

    # optional github actions integration
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        session.install('pytest-github-actions-annotate-failures')

    session.run(
        'pytest',
        '--showlocals', '-vv',
        '--cov', '--cov-config', 'setup.cfg',
        f'--cov-report=html:{htmlcov_output}',
        f'--cov-report=xml:{xmlcov_output}',
        'tests/', *session.posargs
    )
