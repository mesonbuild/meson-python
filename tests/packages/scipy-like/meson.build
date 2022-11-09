project('scipy-like',
  'c', 'cython',
  version: '2.3.4',
)

py_mod = import('python')
py = py_mod.find_installation()

cc = meson.get_compiler('c')
is_windows = host_machine.system() == 'windows'
is_mingw = is_windows and cc.get_id() == 'gcc'
if is_mingw
  # We may be using Mingw in CI, and Cython needs this define when using Mingw
  # together with a MSVC-built Python, see
  # https://github.com/cython/cython/issues/3405
  add_project_arguments('-DMS_WIN64', language: ['c', 'cpp'])
endif

subdir('mypkg')
