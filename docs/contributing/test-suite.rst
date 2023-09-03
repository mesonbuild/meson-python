.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _contributing-test-suite:

**********
Test suite
**********
To run the the test suite you'll need nox__, an automated testing tool for Python.

.. code-block:: console

   $ pip install nox

To run the test suite, run this in your checkout of meson-python:

.. code-block:: console

   $ nox -s tests

This will run the test suite for all the python versions you have installed. Some may fail if they aren't a whole installation. e.g. on Ubuntu 22.04, python3.9 will fail unless you've installed it from the relevant PPA. 

You can run tests for a single python version like this:

.. code-block:: console

   $ nox -s test-3.11

and you can list all the available nox sessions with:

.. code-block:: console

   $ nox -l

__nox : docs/explanations/default-options.rst


.. todo::

   - Explain our most relevant pytest fixtures (``package_*``, ``sdist_*``,
     ``wheel_*``, ``editable_*``, ``venv``, etc.)
