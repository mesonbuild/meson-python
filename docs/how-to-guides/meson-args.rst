.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-meson-args:

**************************
Passing arguments to Meson
**************************

``meson-python`` invokes the ``meson setup``, ``ninja``, and ``meson
install`` commands to build the files that will be included in the
Python wheel, and ``meson dist`` to collect the files that will be
included in the Python sdist. Arguments can be passed to these
commands to modify their behavior. Refer to the `Meson documentation`_
and to the `ninja documentation`_ for details.

.. _Meson documentation: https://mesonbuild.com/Commands.html
.. _ninja documentation: https://ninja-build.org/manual.html#_running_ninja

Command line arguments for ``meson`` and ``ninja`` can be specified
via tool specific settings in ``pyproject.toml`` as lists of strings
for the ``setup``, ``compile``, ``install``, and ``dist`` keys in the
``tool.meson-python.args`` table. For example:

.. code-block:: toml

   [tool.meson-python.args]
   setup = ['-Doption=false', '-Dfeature=enabled', '-Dvalue=42']
   compile = ['-j4']
   install = ['--tags=bindings']
   dist = ['--include-subprojects']

Or can be specified via configuration settings passed by the Python
build front-end as ``setup-args``, ``compile-args``, ``install-args``,
and ``dist-args`` :ref:`config settings <how-to-guides-config-settings>`.
Configuration settings specified via the Python build front-end have
precedence over, and can be used to override, the ones specified in
``pyproject.toml``.

``meson-python`` overrides some of the default Meson options with
:ref:`settings <explanations-default-options>` more appropriate for
building a Python wheel. User options specified via ``pyproject.toml``
or via Python build front-end config settings override the
``meson-python`` defaults.

When building on Windows, ``meson-python`` invokes the ``ninja``
command via the ``meson compile`` wrapper. When the GCC or the LLVM
compilers are not found on the ``$PATH``, this activates the Visual
Studio environment and allows ``ninja`` to use the MSVC compilers. To
activate the Visual Studio environment unconditionally, pass the
``--vsenv`` option to ``meson setup``, see this :ref:`example
<vsenv-example>`. When using the ``meson compile`` wrapper, the user
supplied options for the compilation command are passed via the
``--ninja-args`` option. This ensures that the behaviour is
independent of how the build is initiated. Refer to the `Meson
documentation`__ for more details.

__ https://mesonbuild.com/Commands.html#backend-specific-arguments


Examples
========

Set the default libraries to static
-----------------------------------

Set the default library type to static when building a binary wheel.

To set this option permanently in the project's ``pyproject.toml``:

.. code-block:: toml

   [tool.meson-python.args]
   setup = ['--default-library=static']

To set this option temporarily at build-time:

.. tab-set::

    .. tab-item:: pypa/build
        :sync: key_pypa_build

        .. code-block:: console

           $ python -m build -Csetup-args="--default-library=static" .

    .. tab-item:: pip
        :sync: key_pip

        .. code-block:: console

           $ python -m pip wheel . --config-settings=setup-args="--default-library=static" .


Select the build targets to include in the wheel
------------------------------------------------

It is possible to include in the Python wheel only a subset of the
installable files using Meson `installation tags`_ via the ``meson
install``'s ``--tags`` command line option. When ``--tags`` is
specified, only files that have one of the specified the tags are
going to be installed.

Meson sets predefined tags on some files. Custom installation tags can
be set using the ``install_tag`` keyword argument passed to the target
definition function.  In this example only targets tagged with
``runtime`` or ``python-runtime`` are included in the Python wheel.

.. _installation tags: https://mesonbuild.com/Installing.html#installation-tags

To set this option permanently in the project's ``pyproject.toml``:

.. code-block:: toml

   [tool.meson-python.args]
   install = ['--tags=runtime,python-runtime']

To set this option temporarily at build-time:

.. tab-set::

    .. tab-item:: pypa/build
        :sync: key_pypa_build

        .. code-block:: console

	   $ python -m build -Cinstall-args="--tags=runtime,python-runtime" .

    .. tab-item:: pip
        :sync: key_pip

        .. code-block:: console

	   $ python -m pip wheel . --config-settings=install-args="--tags=runtime,python-runtime" .


Set the build optimization level
--------------------------------

The default compile optimization level when building a binary wheel is
currently set to 2. This can be overwritten by passing the
``-Doptimization`` argument to the ``meson setup`` command.

To set this option permanently in the project's ``pyproject.toml``:

.. code-block:: toml

   [tool.meson-python.args]
   setup = ['-Doptimization=3']

To set this option temporarily at build-time:

.. tab-set::

    .. tab-item:: pypa/build
        :sync: key_pypa_build

        .. code-block:: console

	   $ python -m build -Csetup-args="-Doptimization=3" .

    .. tab-item:: pip
        :sync: key_pip

        .. code-block:: console

	   $ python -m pip wheel . --config-settings=setup-args="-Doptimization=3" .


.. _vsenv-example:

Force the use of the MSVC compilers on Windows
----------------------------------------------

The MSVC compilers are not installed in the ``$PATH``. The Visual
Studio environment needs to be activated for ``ninja`` to be able to
use these compilers. This is taken care of by ``meson compile`` but
only when the GCC compilers or the LLVM compilers are not found on the
``$PATH``. Passing the ``--vsenv`` option to ``meson setup`` forces
the activation of the Visual Studio environment and generates an error
when the activation fails.

This option has no effect on other platforms thus, if your project
requires to be compiled with MSVC, you can consider to set this option
permanently in the project's ``pyproject.toml``:

.. code-block:: toml

   [tool.meson-python.args]
   setup = ['--vsenv']

To set this option temporarily at build-time:

.. tab-set::

    .. tab-item:: pypa/build
        :sync: key_pypa_build

        .. code-block:: console

	   $ python -m build -Csetup-args="--vsenv" .

    .. tab-item:: pip
        :sync: key_pip

        .. code-block:: console

	   $ python -m pip wheel . --config-settings=setup-args="--vsenv" .
