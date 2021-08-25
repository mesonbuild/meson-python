project('mesonpy', version: '0.1.0')

py_mod = import('python')
py = py_mod.find_installation()

if py.language_version().version_compare('< 3.6')
  error('Invalid Python version, only >= 3.6 is supported.')
endif

py.install_sources('mesonpy.py')
