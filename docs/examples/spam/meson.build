project(
  'spam',
  'c',
)

py = import('python').find_installation()

py.install_sources(
  'src/__init__.py',
  'src/bacon.py',
  subdir: 'spam'
)

srcs = files(
  'src/spam.c',
)

py.extension_module(
  'spam',
  srcs,
  install: true,
  subdir: 'spam',
)
