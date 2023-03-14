.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-meson-args:

***************************
Passing arguments to Meson_
***************************

.. todo::

   - Mention the order in which Meson arguments are added, and how it affect
     Meson

Advanced Meson options can be accessed by specifying extra arguments to the
individual Meson commands:

   - meson dist: https://mesonbuild.com/Commands.html#dist
   - meson setup: https://mesonbuild.com/Commands.html#setup
   - meson compile: https://mesonbuild.com/Commands.html#compile
   - meson install: https://mesonbuild.com/Commands.html#install

These arguments can be added permanently to the project by adding a section
to the project's ``pyproject.toml``:

.. code-block:: toml

	[tool.meson-python.args]
	dist    = ['dist-argument_1', 'dist-argument_2', '...']
	setup   = ['setup-argument_1', 'setup-argument_2', '...']
	compile = ['compile-argument_1', 'compile-argument_2', '...']
	install = ['install-argument_1', 'install-argument_2', '...']

They can also be temporarily overwritten at build time using the
:ref:`build config settings<how-to-guides-config-settings>`.

.. tab-set::

    .. tab-item:: pypa/buid
        :sync: key_pypa_build

		.. code-block:: console

			$ python -m build -Cdist-args="args"    \
					  -Csetup-args="args"   \
					  -Ccompile-args="args" \
					  -Cinstall-args="args" .

    .. tab-item:: pip
        :sync: key_pip

		.. code-block:: console

			$ python -m pip --config-settings=dist-args="args"    \
					--config-settings=setup-args="args"   \
					--config-settings=compile-args="args" \
					--config-settings=install-args="args" .


Examples
========

1) Set the default libraries to *static*
------------------------------------------------

Set the default library type to *static* when building a binary wheel.

To set this option permanently in the project's ``pyproject.toml``:

.. code-block:: toml

		[tool.meson-python.args]
		dist = []
		setup = ['--default-library=static']
		compile = []
		install = []

To set this option temporarily at build-time:

.. tab-set::

    .. tab-item:: pypa/build
        :sync: key_pypa_build

        .. code-block:: console

			 $ python -m build -Csetup-args="--default-library=static" .

    .. tab-item:: pip
        :sync: key_pip

        .. code-block:: console

			 $ python -m pip --config-settings=setup-args="--default-library=static" .


2) Use Meson install_tags for selective installs
------------------------------------------------

Meson install_tags can be used (since ``meson-python`` >= 0.13) to select which
targets are installed into the binary wheels. This example causes meson-python
to only install targets tagged with ``runtime`` or ``python-runtime``) into the
binary wheel (ignoring e.g. C++ headers).

To set this option permanently in the project's ``pyproject.toml``:

.. code-block:: toml

			 [tool.meson-python.args]
			 dist = []
			 setup = []
			 compile = []
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

			$ python -m pip --config-settings=install-args="--tags=runtime,python-runtime" .


.. admonition:: Meson installation tags
	:class: seealso

	Each Meson target has a default install_tag (e.g. ``runtime`` for shared
	libraries and ``devel`` for headers.). Calling
	``meson install --tags=tag1,tag2,...`` will cause Meson to only install
	the targets tagged with any of the specified tags. The default tag of
	each target can be overwritten using the target's "install_tag" option.
	For more information refer Mesons documentation in installation-tags:
	https://mesonbuild.com/Installing.html#installation-tags


3) Set the build optimization level to 3
----------------------------------------

The default compile optimization level when building a binary wheel is
currently set to 2. This can be overwritten by passing the
``-Doptimization`` argument to the ``meson setup`` command.

To set this option permanently in the project's ``pyproject.toml``:

.. code-block:: toml

		[tool.meson-python.args]
		dist = []
		setup = ['-Doptimization=3;]
		compile = []
		install = []

To set this option temporarily at build-time:

.. tab-set::

    .. tab-item:: pypa/build
        :sync: key_pypa_build

        .. code-block:: console

			 $ python -m build -Csetup-args="-Doptimization=3" .

    .. tab-item:: pip
        :sync: key_pip

        .. code-block:: console

			 $ python -m pip --config-settings=setup-args="-Doptimization=3" .


.. _Meson: https://github.com/mesonbuild/meson
