project(
    'purelib-and-platlib', 'c',
    version: '1.0.0',
)

py_dep = dependency('python3')
py_mod = import('python')
py = py_mod.find_installation()

py.install_sources('pure.py')
py.extension_module(
    'plat', 'plat.c',
    dependencies: py_dep,
    install: true,
)
