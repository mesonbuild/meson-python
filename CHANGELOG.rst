+++++++++
Changelog
+++++++++


0.9.0 (29-09-2022)
==================

- More fixes on ABI tag detection
- Fix incorrect tag on 32-bit Python running on a x86_64 host
- Fix sdist permissions
- Fix incorrect PyPy tags
- Fix ``install_subdirs`` not being included in wheels
- Take ``MACOSX_DEPLOYMENT_TARGET`` into account for the platform tag
- Don't set the rpath on binaries if unneeded


0.8.1 (28-07-2022)
==================

- Fix ``UnboundLocalError`` in tag detection code


0.8.0 (26-07-2022)
==================

- Fix sometimes the incorrect ABI tags being generated
- Add workaround for macOS 11 and 12 installations that are missing a minor version in the platform string


0.7.0 (22-07-2022)
==================

- Fix the wrong Python and ABI tags being generated in Meson 0.63.0
- Fix project license not being included in the project metadata


0.6.0 (21-06-2022)
==================

- Project relicensed to MIT
- Error out when running in an unsupported interpreter
- Fix slightly broken Debian heuristics
- Update ``pep621`` dependency to ``pyproject-metadata``


0.5.0 (26-05-2022)
==================

- Improvements in dependency detections
- Include uncommited changes in sdists


0.4.0 (06-05-2022)
==================

- Set sane default arguments for release builds


0.3.0 (23-03-2022)
==================

- Initial cross-platform support
  - Bundling libraries stioll is only supported on Linux
- Add initial documentation
- The build directory is now located in the project source


0.2.1 (26-02-2022)
==================

- Fix getting the project version dynamically from Meson


0.2.0 (24-01-2022)
==================

- Select the correct ABI and Python tags
- Force Meson to use the correct Python executable
- Replace auditwheel with in-house vendoring mechanism


0.1.2 (12-11-2021)
==================

- Fix auditwheel not being run


0.1.1 (28-10-2021)
==================

- Fix minor compability issue with Python < 3.9


0.1.0 (28-10-2021)
==================

- Initial release
