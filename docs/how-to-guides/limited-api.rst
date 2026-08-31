.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _howto-limited-api:

***********************************
Targeting the CPython Limited C API
***********************************

This page describes how to configure your package to build against the
CPython `limited API`_ and build `stable ABI`_ wheels. Limited API builds
target a minimum interpreter version and produce a single wheel that
can support newer interpreter versions.

You can enable limited API builds by default or make them opt-in.
We recommend making them opt-in to avoid failures or special handling
when building for interpreters that do not support the stable ABI, such
as free-threaded CPython 3.14. Using the version-specific C API can also
`improve performance`_ for source installations and distribution packages
that do not need the stable ABI.

Compile your extension modules for the limited API by specifying the
``limited_api`` argument to the ``extension_module()`` function in the
Meson Python module. The version passed to ``limited_api`` selects
the limited API your extension uses. Meson converts this version to
the corresponding value of the ``Py_LIMITED_API`` preprocessor macro.

The wheel's :ref:`Python compatibility tag <limited-api-wheel-tags>`
still corresponds to the interpreter used for the build, regardless of
the ``limited_api`` version you select.

Enabling the
:option:`tool.meson-python.limited-api` setting declares that all the
extension modules in your package target the limited API and adjusts the
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


For limited API builds, on platforms where Python extension modules
targeting the stable ABI use a dedicated filename suffix, ``meson-python``
verifies that all the extension modules included in the wheel use the
stable ABI filename suffix and fails the build otherwise.


.. _opt-in-limited-api-example:

Set up Limited API support as opt-in
------------------------------------

To make limited API builds opt-in, add
``python.allow_limited_api=false`` to the ``default_options`` in your
existing ``project()`` call in ``meson.build``:

.. code-block:: meson

   project(
       'example',
       'c',
       default_options: ['python.allow_limited_api=false'],
   )

Keep ``limited-api = true`` in ``pyproject.toml`` and the ``limited_api``
argument to ``extension_module()`` as shown above. When
``python.allow_limited_api`` is false, Meson ignores the ``limited_api``
argument, compiles extension modules for the ABI of the interpreter
used for the build, and produces a wheel tagged as compatible with
the build interpreter.

To build a stable ABI wheel, explicitly enable limited API builds:

.. tab-set::

   .. tab-item:: pypa/build
      :sync: key_pypa_build

      .. code-block:: console

         $ python -m build --wheel -Csetup-args="-Dpython.allow_limited_api=true" .

   .. tab-item:: pip
      :sync: key_pip

      .. code-block:: console

         $ python -m pip wheel -Csetup-args="-Dpython.allow_limited_api=true" .


.. _limited-api-wheel-tags:

Limited API compatibility
-------------------------

``meson-python`` conservatively chooses the wheel's Python compatibility
tag based only on the interpreter used for the build, regardless of the
target ``limited_api`` version.  For example, a wheel built with CPython
3.12 for the 3.10 limited API is tagged ``cp312-abi3`` and can be
installed only on GIL-enabled CPython 3.12 and later. When building
stable ABI wheels for distribution, for example on PyPI, build with the
oldest CPython version you want the wheel to support, as `recommended by
CPython`_.  If you are installing from source into a particular
environment, use that environment's interpreter; you do not need to
build with the oldest supported version.

PyPy supports the limited API, but does not implement a stable ABI, thus
the :option:`tool.meson-python.limited-api` setting has no effect on the
wheel tags when building with PyPy.


The ``abi3t`` stable ABI
------------------------

CPython 3.15 introduces the ``abi3t`` stable ABI. Extension modules built
for ``abi3t`` can be loaded by both the GIL-enabled and the free-threaded
builds of CPython 3.15 and later: a single wheel tagged ``abi3.abi3t``
supports all CPython interpreters from version 3.15 on.

``abi3t`` extension modules require limited API version 3.15 or later
and, currently, a free-threaded interpreter for the build: compiling
for ``abi3t`` with a GIL-enabled interpreter is not supported yet.
Once you have made the source changes described in the
`abi3t migration guide`_, no additional build configuration is required:
the CPython headers select ``abi3t`` when ``Py_LIMITED_API`` is defined
while compiling for a free-threaded interpreter.

Meson refuses a ``limited_api`` version newer than the interpreter
used for the build.  If you build ``abi3`` wheels for older
CPython versions and ``abi3.abi3t`` wheels for CPython 3.15 and later,
you can select the limited API version by querying the ``Py_GIL_DISABLED``
sysconfig variable, which is 1 for free-threaded builds:

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

Free-threaded CPython 3.13 and 3.14 do not support the limited API:
disable limited API builds when using these interpreters.
The :ref:`opt-in configuration above <opt-in-limited-api-example>`
disables them by default.

.. _limited API: https://docs.python.org/3/c-api/stable.html#limited-c-api
.. _stable ABI: https://docs.python.org/3/c-api/stable.html#stable-application-binary-interface
.. _recommended by CPython: https://docs.python.org/3/c-api/stable.html#limited-api-caveats
.. _improve performance: https://docs.python.org/3/c-api/stable.html#limited-api-scope-and-performance
.. _abi3t migration guide: https://docs.python.org/3.15/howto/abi3t-migration.html
