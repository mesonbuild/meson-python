project(
    'imports-itself-during-build', 'c',
    version: '1.0.0',
)

py_mod = import('python')
py = py_mod.find_installation()

py.install_sources('pure.py')
py.extension_module(
    'plat', 'plat.c',
    install: true,
)

run_command(py, '-c', 'import pure')
