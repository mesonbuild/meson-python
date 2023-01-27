.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-config-settings:

*************************
Use build config settings
*************************

Build config settings are settings you can pass to ``meson-python`` when
building your project. They can be use to customize the build in some aspect.

The way you specify them depends on which tool you are using, here are the most
popular ones.


`pypa/build`_
=============

On `pypa/build`_, they can be used via the ``-C``/``--config-setting`` option.


.. code-block:: console

   $ python -m build -Ckey=value


Please check the `pypa/build documentation`_ for more information.


pip_
====

On `pip`_, they can be used via the ``--config-settings`` option.


.. code-block:: console

   $ pip install . --config-settings key=value


Please check the `pip documentation`_ for more information.


.. _pypa/build: https://github.com/pypa/build
.. _pypa/build documentation: https://pypa-build.readthedocs.io/en/stable/
.. _pip: https://github.com/pypa/pip
.. _pip documentation: https://pip.pypa.io/
