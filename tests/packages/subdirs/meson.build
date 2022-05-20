project(
    'subdirs',
    version: '1.0.0',
)

py_mod = import('python')
py = py_mod.find_installation()

py.install_sources([
    'subdirs' / '__init__.py',
    'subdirs' / 'a' / '__init__.py',
    'subdirs' / 'a' / 'b' / 'c.py',
    'subdirs' / 'b' / 'c.py',
])
