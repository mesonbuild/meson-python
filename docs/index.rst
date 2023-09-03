.. SPDX-FileCopyrightText: 2022 The meson-python developers
..
.. SPDX-License-Identifier: MIT


************
meson-python
************

.. highlights::

   ``meson-python`` is a Python build backend built on top of the Meson
   build-system. It enables you to use Meson for your Python packages.


Want to look at examples in real projects? Check out our curated list of
``meson-python`` projects :ref:`here <projects-using-meson-python>`.


Where to start?
===============

If you are new to Python packaging, we recommend you check our
:ref:`tutorial-introduction` tutorial, which walks you through creating and
releasing your first Python package.


If you are already familiar with Python packaging, we recommend you check
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


.. toctree::
   :caption: Tutorials
   :hidden:

   tutorials/introduction

.. tutorials/entrypoints
   tutorials/executable


.. toctree::
   :caption: How to guides
   :hidden:

   how-to-guides/first-project
   how-to-guides/editable-installs
   how-to-guides/config-settings
   how-to-guides/meson-args
   how-to-guides/debug-builds
   projects-using-meson-python

.. how-to-guides/build-directory


.. toctree::
   :caption: Reference
   :hidden:

   reference/config-settings
   reference/pyproject-settings
   reference/environment-variables
   explanations/default-options
   reference/limitations
   reference/meson-compatibility

.. reference/quirks


..
   toctree::
   :caption: Explanations
   :hidden:

   explanations/design
   explanations/internal-dependencies
   explanations/editable-installs


.. toctree::
   :caption: Project
   :hidden:

   changelog
   about
   contributing/index
   Source Code <https://github.com/mesonbuild/meson-python>
   Issue Tracker <https://github.com/mesonbuild/meson-python/issues>


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
