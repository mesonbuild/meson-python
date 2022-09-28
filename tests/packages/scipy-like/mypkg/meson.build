generate_version = custom_target('generate-config-file',
  install: true,
  build_always_stale: true,
  build_by_default: true,
  output: '__config__.py',
  input: '../tools/generate_config.py',
  command: [py, '@INPUT@', '@OUTPUT@'],
  install_dir: py.get_install_dir(pure: false) / 'mypkg'
)

py.extension_module('extmod',
  'extmod.c',
  install: true,
  subdir: 'mypkg'
)

py.extension_module('cy_extmod',
  'cy_extmod.pyx',
  install: true,
  subdir: 'mypkg'
)

py.install_sources(
  '__init__.py',
  pure: false,
  subdir: 'mypkg'
)

# Still broken, see gh-105 and https://github.com/mesonbuild/meson/issues/10639
install_subdir(
  'submod',
  install_dir: py.get_install_dir(pure: false) / 'mypkg'
)
