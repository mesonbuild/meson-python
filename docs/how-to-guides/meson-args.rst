.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-meson-args:

**************************
Passing arguments to Meson
**************************

``meson-python`` invokes the ``meson setup``, ``ninja``, and ``meson
install`` to build the files that will be included in the Python
wheel, and ``meson dist`` to collect the files that will be included
in the Python sdist. Commans line options can be passed to these
commands to alther their behavior, either via tool specific settings
in ``pyptoject.toml`` or via the Python build front-end command
line. Options specified via the Python build front-end command line
override the ones specified in ``pyproject.toml``.

Command line arguments can be specified in ``pyproject.toml`` as lists
of strings in the ``tool.meson-python.args`` table. Example:

.. code-block:: toml

   [tool.meson-python.args]
   dist = ['--include-subprojects']
   setup = ['-Doption=false', '-Dfeature=enable', '-Dvalue=42']
   compile = ['-j4']
   install = ['--tags=bindings']

They can also be temporarily overwritten at build time using the
:ref:`build config settings<how-to-guides-config-settings>`:

.. tab-set::

    .. tab-item:: pypa/buid
        :sync: key_pypa_build

	.. code-block:: console

	   $ python -m build \
               -Csetup-args="-Doption=true" \
               -Csetup-args="-Dvalue=1" \
               -Ccompile-args="-j6"

    .. tab-item:: pip
        :sync: key_pip

	.. code-block:: console

	   $ python -m pip wheel . \
               --config-settings=setup-args="-Doption=disable" \
               --config-settings=compile-args="-j6"

This examples use the ``python -m pip wheel`` command to build a
Python wheel that can be later installed or distributed. To build a
package and immediately install it, just replace ``wheel`` with
``install``.

Please note while ``pypa/build`` concatenates arguments for the same
key passed to the ``-C`` option, ``pip`` at least up to version 23.0.1
does not offer any way to set a build config setting to a list of
strings: later values for the same key passed to ``--config-settings``
override earlier ones. This effectively limits the number of options
that can be passed to each command invoked in the build process to
one. This limitation is tracked in `pip issue #11681`_.

.. _pip issue #11681: https://github.com/pypa/pip/issues/11681


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


Use Meson installation tags to select the build targets to include
------------------------------------------------------------------

It is possible to include in the Python wheel only a subset of the
installable files using Meson `installation tags`_ via the ``meson
install``'s ``--tags`` command line option. When ``--tags`` is
specified, only files that have been tagged with one of the tags are
going to be installed. Meson sets predefined tags on some
files. Custom installation tag can be set using the ``install_tag``
keyword argument passed to the target definition function.  In this
example only targets tagged with ``runtime`` or ``python-runtime`` are
included in the Python wheel.

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

	   $ python -m build -install-args="--tags=runtime,python-runtime" .

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
