import subprocess

from .conftest import build_project_wheel, examples_dir


def test_build_and_import(virtual_env, tmp_dir_session):
    """Test that the wheel for the spam example builds, installs, and imports."""
    wheel = build_project_wheel(
        package=examples_dir / 'spam',
        outdir=tmp_dir_session
    )

    subprocess.check_call([virtual_env, '-m', 'pip', '-qqq', 'install', wheel])
    output, status = subprocess.check_output(
        [virtual_env, '-c', f'import spam; print(spam.system("ls {wheel}"))']
    ).decode().strip().split('\n')

    assert output == str(wheel)
    assert int(status) == 0
