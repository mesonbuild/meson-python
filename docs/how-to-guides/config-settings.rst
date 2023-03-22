.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-config-settings:

*************************
Use build config settings
*************************

Build config settings are settings you can pass to ``meson-python`` when
building your project. They can be use to customize the build in some
aspect.

Several Python build front-ends exist, with different ways to pass
configuration settings to the build back-end. The most popular are
`pypa/build`_, which uses the ``-C`` command line option, and `pip`_,
which uses the ``--config-settings`` option. For example:

.. _pypa/build: https://github.com/pypa/build
.. _pip: https://github.com/pypa/pip

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

This examples use the ``python -m pip wheel`` command to build a Python
wheel that can be later installed or distributed. To build a package and
immediately install it, just replace ``wheel`` with ``install``.

See the :ref:`how-to-guides-meson-args` guide for more examples. Refer to
the `pypa/build documentation`_ or to the `pip documentation`_ for more
information.

.. _pypa/build documentation: https://pypa-build.readthedocs.io/en/stable/
.. _pip documentation: https://pip.pypa.io/

.. admonition:: Passing multiple settings
   :class: caution

   Please note that, while ``pypa/build`` concatenates arguments for the
   same key passed to the ``-C`` option, ``pip`` up to version 23.0.1 does
   not offer any way to set a build config setting to a list of strings:
   later values for the same key passed to ``--config-settings`` override
   earlier ones.

   This effectively limits the number of options that can be passed to each
   command invoked in the build process to one. This limitation is tracked
   in `pip issue #11681`_. This limitation should be removed in the next
   version of pip.

.. _pip issue #11681: https://github.com/pypa/pip/issues/11681
