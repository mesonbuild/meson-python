.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _howto-limited-api:

***********************************
Targeting the CPython Limited C API
***********************************

This page describes how to configure your project to build against the
CPython `limited API`_ and build `stable ABI`_ wheels. Limited API builds
target a minimum interpreter version and produce a single wheel that
can support newer interpreter versions.

Enabling the :option:`tool.meson-python.limited-api` setting declares that all
the extension modules in the package target the limited API and adjusts the
wheel filename ABI tag accordingly:

.. code-block:: meson

   py = import('python').find_installation(pure: false)

   py.extension_module(
       '_core',
       '_core.c',
       limited_api: '3.10',
       install: true,
       subdir: 'example',
   )

.. code-block:: toml

   [tool.meson-python]
   limited-api = true

Build with the minimum CPython interpreter version you wish to
support. ``meson-python`` verifies that all the extension modules
included in the wheel use the stable ABI filename suffix and fails the
build otherwise. PyPy does not support the limited API thus this setting
has no effect when building with PyPy.


The ``abi3t`` stable ABI
------------------------

CPython 3.15 introduces the ``abi3t`` stable ABI, see :pep:`803` and the
`abi3t migration guide`_.  Extension modules built for ``abi3t`` can be
loaded by both the GIL-enabled and the free-threaded builds of CPython
3.15 and later: a single wheel tagged ``abi3.abi3t`` supports all
CPython interpreters from version 3.15 on.

``abi3t`` extension modules require limited API version 3.15 or later and a
free-threaded interpreter for the build.  Building abi3t extensions using a
GIL-enabled interpreter is not currently support. Nothing else is required: the
CPython headers select ``abi3t`` when ``Py_LIMITED_API`` is defined while
compiling for a free-threaded interpreter.

Meson refuses a ``limited_api`` version newer than the interpreter used
for the build.  Projects that build ``abi3`` wheels for older CPython
versions and ``abi3.abi3t`` wheels for CPython 3.15 and later can select
the limited API version querying the ``Py_GIL_DISABLED`` sysconfig
variable, which is 1 for free-threaded builds:

.. code-block:: meson

   py = import('python').find_installation(pure: false)

   limited_api = '3.10'
   if py.language_version().version_compare('>=3.15')
       if py.get_variable('Py_GIL_DISABLED') == 1
           limited_api = '3.15'
       endif
   endif

   py.extension_module(
       '_core',
       '_core.c',
       limited_api: limited_api,
       install: true,
       subdir: 'example',
   )

Disable the Limited API
-----------------------

Projects that enable the :option:`tool.meson-python.limited-api` setting in
their ``pyproject.toml`` opt into limited API builds by default. Passing the
``-Dpython.allow_limited_api=false`` option to ``meson setup`` disables
this default. Instead, extension modules are compiled for the ABI
specific to the Python version used for the build and the wheel is tagged
accordingly. This is required to build wheels for free-threaded CPython 3.13
and 3.14. Opting out of limited API builds may also `improve performance`_.

To disable limited API builds temporarily at build-time:

.. tab-set::

   .. tab-item:: pypa/build
      :sync: key_pypa_build

      .. code-block:: console

         $ python -m build --wheel -Csetup-args="-Dpython.allow_limited_api=false" .

   .. tab-item:: pip
      :sync: key_pip

      .. code-block:: console

         $ python -m pip wheel -Csetup-args="-Dpython.allow_limited_api=false" .

To set this option only when building wheels for free-threaded CPython
3.14 in CI using cibuildwheel:

.. code-block:: toml

   [[tool.cibuildwheel.overrides]]
   select = "cp314t-*"
   config-settings = { setup-args = ["-Dpython.allow_limited_api=false"] }

.. _limited API: https://docs.python.org/3/c-api/stable.html#limited-c-api
.. _stable ABI: https://docs.python.org/3/c-api/stable.html#stable-application-binary-interface
.. _abi3t migration guide: https://docs.python.org/3.15/howto/abi3t-migration.html
.. _improve performance: https://docs.python.org/3/c-api/stable.html#limited-api-scope-and-performance
