.. SPDX-FileCopyrightText: 2024 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _shared-libraries:

**********************
Using shared libraries
**********************

Python projects may build shared libraries as part of their project, or link
with shared libraries from a dependency. This tends to be a common source of
issues, hence this page aims to explain how to include shared libraries in
wheels, any limitations and gotchas, and how support is implemented in
``meson-python`` under the hood.

We distinguish between *internal* shared libraries that are built as part of
the project, and *external* shared libraries that are provided by project
dependencies and that are linked with the project build artifacts.
For internal shared libraries, we also distinguish whether the shared library
is being installed to its default system location (typically
``/usr/local/lib`` on Unix-like systems, and ``C:\\lib`` on Windows - we call
this ``libdir`` in this guide) or to a location in ``site-packages`` within the
Python package install tree. All these scenarios are (or will be) supported,
with some caveats:

+-----------------------+------------------+------------+-------+-------+
| shared library source | install location | Windows    | macOS | Linux |
+=======================+==================+============+=======+=======+
| internal              | libdir           | ✓ :sup:`1` | ✓     | ✓     |
+-----------------------+------------------+------------+-------+-------+
| internal              | site-packages    | ✓          | ✓     | ✓     |
+-----------------------+------------------+------------+-------+-------+
| external              | ---              | ✓ :sup:`2` | ✓     | ✓     |
+-----------------------+------------------+------------+-------+-------+

.. TODO: add subproject as a source

1. Support for internal shared libraries on Windows is enabled with the
   :option:`tool.meson-python.allow-windows-internal-shared-libs` option and
   requires cooperation from the package to extend the DLL search path or
   preload the required libraries. See below for more details.

2. External shared libraries require ``delvewheel`` usage on Windows (or some
   equivalent way, like amending the DLL search path to include the directory
   in which the external shared library is located). Due to the lack of
   `RPATH <https://en.wikipedia.org/wiki/Rpath>`__ support on Windows, there is
   no good way around this.

.. _internal-shared-libraries:

Internal shared libraries
=========================

A shared library produced by ``library()`` or ``shared_library()`` built like this

.. code-block:: meson

    example_lib = shared_library(
        'example',
        'examplelib.c',
        install: true,
    )

is installed to ``libdir`` by default. If the only reason the shared library exists
is to be used inside the Python package being built, then it is best to modify
the install location, via the ``install_dir`` argument, to be within
the Python package itself:

.. TODO update the text block below to 'meson' when
.. meson lexer is updated to fix
.. https://github.com/pygments/pygments/issues/2918

.. code-block:: text

    example_lib = shared_library(
        'example',
        'examplelib.c',
        install: true,
        install_dir: py.get_install_dir() / 'mypkg/subdir',
    )

Then an extension module in the same install directory can link against the
shared library in a portable manner by using ``install_rpath``:

.. code-block:: meson

    py.extension_module('_extmodule',
        '_extmodule.c',
        link_with: example_lib,
        install: true,
        subdir: 'mypkg/subdir',
        install_rpath: '$ORIGIN'
    )

The above method will work as advertised on macOS and Linux; ``meson-python`` does
nothing special for this case. Windows needs some special handling though, due to
the lack of RPATH support:

.. literalinclude:: ../../tests/packages/sharedlib-in-package/mypkg/__init__.py
   :start-after: start-literalinclude
   :end-before: end-literalinclude

If an internal shared library is not only used as part of a Python package,
but for example also as a regular shared library then the method shown above
won't work. The library is then marked for installation into the system
default ``libdir`` location.  Actually installing into ``libdir`` isn't
possible with wheels, hence ``meson-python`` will instead do the following:

1. Install the shared library to the ``.<project-name>.mesonpy.libs``
   top-level directory in the wheel, which on install will end up in
   ``site-packages``.
2. On platforms other than Windows, rewrite RPATH entries for install targets
   that depend on the shared library to point to that new install location
   instead.

On platforms other than Windows, this will make the shared library work
automatically, with no other action needed from the package author. On
Windows, due to the lack of RPATH support, the ``.<project-name>.mesonpy.libs``
location search path needs to be added to the DLL search path, with code
similar to the one presented above. For this reason, handling of internal
shared libraries on Windows is conditional to setting the
:option:`tool.meson-python.allow-windows-internal-shared-libs` option.


External shared libraries
=========================

External shared libraries are installed somewhere on the build machine, and
usually detected by a ``dependency()`` or ``compiler.find_library()`` call in a
``meson.build`` file. When a Python extension module or executable uses the
dependency, the shared library will be linked against at build time.

If the shared library is located in a directory on the loader search path,
the wheel created by ``meson-python`` will work locally when installed.
If it's in a non-standard location however, the shared library will go
missing at runtime. The Python extension module linked against it needs an
RPATH entry - and Meson will not automatically manage RPATH entries for you.
Hence you'll need to add the needed RPATH yourself, for example by adding
``-Wl,rpath=/path/to/dir/sharedlib/is/in`` to ``LDFLAGS`` before starting
the build. In case you run into this problem after a wheel is built and
installed, adding that same path to the ``LD_LIBRARY_PATH`` environment variable is a quick way of
checking if that is indeed the problem.

On Windows, the solution is similar - the shared library can either be
preloaded, or the directory that the library is located in added to the DLL
search path with ``os.add_dll_directory``, or vendored into the wheel with
``delvewheel`` in order to make the built Python package usable locally.

Publishing wheels which depend on external shared libraries
-----------------------------------------------------------

On all platforms, wheels which depend on external shared libraries usually need
post-processing to make them usable on machines other than the one on which
they were built. This is because the RPATH entry for an external shared library
contains a path specific to the build machine. This post-processing is done by
tools like ``auditwheel`` (Linux), ``delvewheel`` (Windows), ``delocate``
(macOS) or ``repair-wheel`` (any platform, wraps the other tools).

Running any of those tools on a wheel produced by ``meson-python`` will vendor
the external shared library into the wheel and rewrite the RPATH entries (it
may also do some other things, like symbol mangling).

On Windows, the package author may also have to add the preloading like shown
above with ``_append_to_sharedlib_load_path()`` to the main ``__init__.py`` of
the package, ``delvewheel`` may or may not take care of this (please check its
documentation if your shared library goes missing at runtime).

Note that we don't cover using shared libraries contained in another wheel
and depending on such a wheel at runtime in this guide. This is inherently
complex and not recommended (you need to be in control of both packages, or
upgrades may be impossible/breaking).


Using libraries from a Meson subproject
=======================================

It can often be useful to build a shared library in a
`Meson subproject <https://mesonbuild.com/Subprojects.html>`__, for example as
a fallback in case an external dependency isn't detected. There are two main
strategies for folding a library built in a subproject into a wheel built with
``meson-python``:

1. Build the library as a static library instead of a shared library, and
   link it into a Python extension module that needs it.
2. Build the library as a shared library, and either change its install path
   to be within the Python package's tree, or rely on ``meson-python`` to fold
   it into the wheel when it'd otherwise be installed to ``libdir``.

Static linking tends to be easier, and it is the recommended solution, unless
the library of interest cannot be built as a static library or it would
inflate the wheel size too much because it's needed by multiple Python
extension modules.

Static library from subproject
------------------------------

The major advantage of building a library target as static and folding it
directly into an extension module is that the RPATH or the DLL search path do
not need to be adjusted and no targets from the subproject need to be
installed. To ensures that ``library()`` targets are built as static, and that
no parts of the subprojects are installed, the following configuration can be
added in ``pyproject.toml`` to ensure the relevant options are passed to Meson:

.. code-block:: toml

    [tool.meson-python.args]
    setup = ['--default-library=static']
    install = ['--skip-subprojects']

To then link against the static library in the subproject, say for a subproject
named ``bar`` with the main library target contained in a ``bar_dep`` dependency,
add this to your ``meson.build`` file:

.. code-block:: meson

    bar_proj = subproject('bar')
    bar_dep = bar_proj.get_variable('bar_dep')

    py.extension_module(
        '_example',
        '_examplemod.c',
        dependencies: bar_dep,
        install: true,
    )

Shared library from subproject
------------------------------

Sometimes it may be necessary or preferable to use dynamic linking to a shared
library provided in a subproject, for example to avoid inflating the wheel
size having multiple copies of the same object code in different extension
modules using the same library. In this case, the subproject needs to install
the shared library in the usual location in ``libdir``.  ``meson-python``
will automatically include it into the wheel in
``.<project-name>.mesonpy.libs`` just like an internal shared library.

Most projects, however, install more than the shared library and the extra
components, such as header files or documentation, should not be included in
the Python wheel. Projects may have configuration options to disable building
and installing additional components, in this case, these options can be
passed to the ``subproject()`` call:

.. code-block:: meson

    foo_subproj = subproject('foo',
        default_options: {
            'docs': 'disabled',
        })
    foo_dep = foo_subproj.get_variable('foo_dep')

Install tags do not work per subproject, therefore to exclude other parts of
the subproject from being included in the wheel, we need to resort to
``meson-python`` install location filters using the
:option:`tool.meson-python.wheel.exclude` build option:

.. code-block:: toml

    [tool.meson-python.wheel]
    exclude = ['{prefix}/include/*']
