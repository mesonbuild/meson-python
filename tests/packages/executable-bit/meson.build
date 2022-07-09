project(
    'executable-bit', 'c',
    version: '1.0.0',
)

py_mod = import('python')
py = py_mod.find_installation()

executable(
    'example', 'example.c',
    install: true,
)

install_data(
    'example-script.py',
    rename: 'example-script',
    install_dir: get_option('bindir'),
)

py.install_sources('executable_module.py')
