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
distribution to other code or users. Most notably, the ``console_scripts``
entry points will create a command line wrapper.

See the `PyPA documentation on entry points <https://packaging.python.org/en/latest/specifications/entry-points/>`_.

Using entry points with meson-python
====================================

Entry points are defined in the ``pyproject.toml`` `metadata specification
<https://packaging.python.org/en/latest/specifications/declaring-project-metadata/#entry-points>`_.
No further configuration is required when using ``meson-python``.

Console entry point
-------------------

To show the usage of console entry points we build a simple
python script:

.. code-block:: python
   :caption: src/simpleapp/console.py

    """
    Simple test application.

    Usage:
        simpleapp --help
        simpleapp doc
        simpleapp run [<file>] [options]

    Options:
        -h --help                                   display this help message
        --workdir-path=<workdir-path>               directory in which to run [default: none]

    """
    import docopt



    def main():
        args = docopt.docopt(__doc__)
        # Just print the arguments for now.
        print(args)

    if __name__ == "__main__":
        main()

This script will be part of a larger python package (called ``simpleapp``).
The meson build file is very simple and only installs the python sources.

.. code-block:: meson
   :caption: meson.build

    project('simpleapp', version:'0.0.1')


    pymod = import('python')
    python = pymod.find_installation('python3')
    pydep = python.dependency()

    python.install_sources(
      'src/simpleapp/__init__.py', 'src/simpleapp/console.py'
      , pure: true
      , subdir: 'simpleapp'
    )

The entry points are then specified in the ``pyproject.toml`` metadata specification.


.. code-block:: toml
   :caption: pyproject.toml

    [project]
    name = "simpleapp"
    description = "simple app"
    requires-python = ">=3.6"
    dependencies = ["docopt"]
    version = "0.0.1"

    [project.scripts]
    simpleapp = "simpleapp.console:main"

    [build-system]
    requires = ["meson", "toml", "ninja", "meson-python"]
    build-backend = 'mesonpy'
