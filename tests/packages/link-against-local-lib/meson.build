project(
    'link-against-local-lib', 'c',
    version: '1.0.0',
)

example_lib = shared_library(
    'example', 'examplelib.c',
    install: true,
)

py_mod = import('python')
py = py_mod.find_installation()

py.extension_module(
    'example', 'examplemod.c',
    link_with: example_lib,
    install: true,
)
