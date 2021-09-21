project(
    'configure-data',
    version: '1.0.0',
)

py_mod = import('python')
py = py_mod.find_installation()

configure_file(
    input: 'configure_data.py.in',
    output: 'configure_data.py',
    configuration: configuration_data({
        'MSG': 'hello!',
    }),
    install_dir: py.get_install_dir(),
)
