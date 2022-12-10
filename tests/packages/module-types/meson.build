project(
    'module-types', 'c',
    version: '1.0.0',
)

py_mod = import('python')
py = py_mod.find_installation()

py.install_sources('file.py')
py.install_sources(
    'package' / '__init__.py',
    subdir: 'package',
)
py.install_sources(
    'namespace' / 'data.py',
    subdir: 'namespace',
)
py.extension_module(
    'native', 'native.c',
    install: true,
)
