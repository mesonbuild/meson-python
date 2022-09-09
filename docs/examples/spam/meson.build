project(
  'spam',
  'c',
)

py_mod = import('python')
py = py_mod.find_installation()

# Specify directories to be included - usually this is where your header files live.
# Note that specifying the path to Python.h is not necessary with meson-python.
includes = include_directories(
  [
    'src'
  ]
)

srcs = [
  'src/spammodule.c',
]

# If some files (such as .py files) need to be copied to site-packages,
# this is where they get specified. Files get copied to
# <python directory>/site-packages/<subdir>
py.install_sources(
  [
    'src/__init__.py'
  ],
  subdir: 'spam'
)

py.extension_module(
  '_spam',
  srcs,
  install: true,
  subdir: 'spam',
  include_directories: includes
)
