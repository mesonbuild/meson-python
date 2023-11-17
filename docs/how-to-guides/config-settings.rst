.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-config-settings:

***************************
Using build config settings
***************************

Build config settings can be used to customize some aspects of the
build. See the :doc:`../reference/config-settings` reference for a list
of the settings implemented by ``meson-python``.

How build config settings are specified depends on the Python package
build front-end used. The most popular build front-end are `build`_ and
`pip`_. These use the ``--config-settings`` long command line option or
the ``-C`` short command line option:

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


Refer to the `build`_ and `pip`_ documentation for details.  This
example uses the ``python -m pip wheel`` command to build a Python wheel
that can be later installed or distributed. To build a package and
immediately install it, replace ``wheel`` with ``install``.  See the
:ref:`how-to-guides-meson-args` guide for more examples.


.. admonition:: Passing multiple settings
   :class: caution

   Please note that ``pip`` prior to 23.1 did not offer a way to set a
   build config setting to a list of strings: later values for the
   same key passed to ``--config-settings`` override earlier ones,
   effectively limiting the number of options that can be passed to
   each command invoked in the build process to one. This limitation
   has been lifted in ``pip`` release 23.1.


.. _build: https://pypa-build.readthedocs.io/en/stable/
.. _pip: https://pip.pypa.io/
