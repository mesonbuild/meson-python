.. SPDX-FileCopyrightText: 2022 The meson-python developers
..
.. SPDX-License-Identifier: MIT


*************************
meson-python |PyPI badge|
*************************

.. image:: https://results.pre-commit.ci/badge/github/mesonbuild/meson-python/main.svg
   :target: https://results.pre-commit.ci/latest/github/mesonbuild/meson-python/main
   :alt: pre-commit.ci status


.. image:: https://github.com/mesonbuild/meson-python/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/mesonbuild/meson-python/actions/workflows/tests.yml
   :alt: Github Action 'tests' workflow status


.. image:: https://codecov.io/gh/mesonbuild/meson-python/branch/main/graph/badge.svg?token=xcb2u2YvVk
   :target: https://codecov.io/gh/mesonbuild/meson-python
   :alt: Codecov coverage status


.. image:: https://readthedocs.org/projects/meson-python/badge/?version=stable
   :target: https://meson-python.readthedocs.io/en/stable/?badge=stable
   :alt: Documentation Status


.. highlights::

   ``meson-python`` is a Python build backend built on top of the Meson_
   build-system. It enables you to use Meson_ for your Python packages.


Want to look at examples in real projects? Check out our curated list of
``meson-python`` projects :ref:`here <projects-using-meson-python>`.


Where to start?
===============


New to Python packaging
-----------------------

If you are new to Python packaging, we recommend you check our
:ref:`tutorial-introduction` tutorial, which walks you through creating and
releasing your first Python package.


Experienced users
-----------------

If you are already familiarized with Python packaging, we recommend you check
our :ref:`how-to-guides-first-project` guide, which shows you how to quickly
setup a ``meson-python`` project.


How to reach us?
================

``meson-python`` is an open source project, so all support is at a best-effort
capacity, but we are happy to help where we can.

If you have a general question feel free to `start a discussion`_ on Github. If
you want to report a bug, request a feature, or propose an improvement, feel
free to open an issue on our bugtracker_.


.. admonition:: Search first!
   :class: tip

   Before starting a discussion, please try searching our bugtracker_ and
   `discussion page`_ first.


In addition, the `#meson-python`_ channel on the `PyPA Discord`_ may be useful
for quick questions - one ``meson-python`` maintainer is active there.


Contributors
============

..  contributors:: mesonbuild/meson-python
   :avatars:
   :exclude: pre-commit-ci[bot]


.. toctree::
   :caption: Information
   :hidden:

   changelog
   projects-using-meson-python
   security


.. toctree::
   :caption: Tutorials
   :hidden:

   tutorials/introduction
   tutorials/data
   tutorials/entrypoints
   tutorials/executable


.. toctree::
   :caption: How to guides
   :hidden:

   how-to-guides/first-project
   how-to-guides/add-dependencies
   how-to-guides/editable-installs
   how-to-guides/config-settings
   how-to-guides/meson-args
   how-to-guides/build-directory
   how-to-guides/executable-with-internal-dependencies


.. toctree::
   :caption: Reference
   :hidden:

   reference/config-settings
   reference/pyproject-settings
   reference/environment-variables
   reference/quirks
   reference/limitations


.. toctree::
   :caption: Explanations
   :hidden:

   explanations/design
   explanations/default-options
   explanations/internal-dependencies
   explanations/editable-installs


.. toctree::
   :caption: Contributing
   :hidden:

   contributing/getting-started
   contributing/commit-format
   contributing/test-suite
   contributing/documentation
   contributing/release-process


.. toctree::
   :caption: Project Links
   :hidden:

   Source Code <https://github.com/mesonbuild/meson-python>
   Issue Tracker <https://github.com/mesonbuild/meson-python/issues>


.. |PyPI badge| image:: https://badge.fury.io/py/meson-python.svg
   :target: https://pypi.org/project/meson-python
   :alt: PyPI version badge


.. _Meson: https://github.com/mesonbuild/meson
.. _getting started: usage/start.html
.. _pip: https://github.com/pypa/pip
.. _pypa/build: https://github.com/pypa/build
.. _build options page: usage/build-options.html
.. _install_data: https://mesonbuild.com/Reference-manual_functions.html#install_data
.. _start a discussion: https://github.com/mesonbuild/meson-python/discussions/new/choose
.. _bugtracker: https://github.com/mesonbuild/meson-python/issues
.. _discussion page: https://github.com/mesonbuild/meson-python/discussions
.. _#meson-python: https://discord.com/channels/803025117553754132/1040322863930024057
.. _PyPA Discord: https://discord.gg/pypa

.. |install_data| replace:: ``install_data``
