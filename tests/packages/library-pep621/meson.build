project('library-pep621', 'c')

example_lib = shared_library(
    'example', 'examplelib.c',
    install: true,
)

executable(
    'example', 'example.c',
    link_with: example_lib,
    install: true,
)
