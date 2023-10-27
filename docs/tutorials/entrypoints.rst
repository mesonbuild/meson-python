.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _tutorials-entrypoints:

************
Entry points
************

.. todo::

   - Give an example of a custom entry point
     - Mention pluggy maybe for an example use-case?

Introduction
============

Entry points provide a mechanism to advertise components of an installed
distribution to other code or users. There are three type of entry-points:
those that provide commands to execute in a shell (``project.scripts``),
commands to launch a GUI (``project.gui-scripts``), and discoverable (plugin
style) entry-points (``project.entry-points.<name>``).

See the `PyPA documentation on entry points <https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#declaring-project-metadata>`_.

Using entry points with meson-python
====================================

Entry points are defined in the ``pyproject.toml`` `metadata specification
<https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#entry-points>`_.
No further configuration is required when using ``meson-python``.

Console entry point
-------------------

To show the usage of console entry points we build a simple python script that
simply prints the arguments it was called with:

.. code-block:: python
   :caption: src/simpleapp/console.py

    """
    Simple test application. Just prints the arguments.
    """


    import argparse


    def main():
        parser = argparse.ArgumentParser(prog='simpleapp', description=__doc__)
        parser.add_argument('doc', action='store_true')

        args = parser.parse_args()

        # Just print the arguments for now.
        print(args)


    if __name__ == "__main__":
        main()

This script will be part of a larger python package (called ``simpleapp``).
The meson build file is very simple and only installs the python sources.

.. code-block:: meson
   :caption: meson.build

    project('simpleapp', version:'0.0.1')


    py = import('python').find_installation('python3')
    py_dep = py.dependency()

    py.install_sources(
      ['src/simpleapp/__init__.py', 'src/simpleapp/console.py']
      , subdir: 'simpleapp'
    )

The entry points are then specified in the ``pyproject.toml`` metadata specification.


.. code-block:: toml
   :caption: pyproject.toml

    [project]
    name = "simpleapp"
    description = "simple app"
    requires-python = ">=3.6"
    version = "0.0.1"

    [build-system]
    build-backend = 'mesonpy'
    requires = ["meson-python"]

    [project.scripts]
    simpleapp = "simpleapp.console:main"
