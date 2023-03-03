.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-first-project:

*************
First project
*************


.. admonition:: Advanced guide
   :class: caution

   This guide assumes you are already familiarized with Python packaging! If you
   aren't, we recommend you check our :ref:`tutorial-introduction` tutorial
   instead.


Specifying the backend
======================

Our build backend is called ``mesonpy``, and that's what you should specify in
the ``build-system.build-backend`` key of ``pyproject-toml``.

You should add ``meson-python``, and all other build dependencies (eg. Cython_)
needed by your Meson_ project, in the ``build-system.requires`` key.


Example
-------

.. code-block:: toml
   :caption: pyproject.toml

   [build-system]
   build-backend = 'mesonpy'
   requires = ['meson-python', 'cython']


Specifying the project metadata
===============================

We use the standard metadata format in the ``project`` section of
``pyproject.toml``.

Please refer to the `relevant PyPA documentation page`_ for a full
specification.


Example
=======


.. code-block:: toml
   :caption: pyproject.toml

   [build-system]
   build-backend = 'mesonpy'
   requires = ['meson-python', 'cython']

   [project]
   name = 'example-package'
   version = '1.0.0'
   description = 'Our example package using meson-python!'
   readme = 'README.md'
   requires-python = '>=3.8'
   license = {file = 'LICENSE.txt'}
   authors = [
     {name = 'Bowsette Koopa', email = 'bowsette@example.com'},
   ]


.. _Cython: https://github.com/cython/cython
.. _Meson: https://mesonbuild.com/
.. _relevant PyPA documentation page: https://packaging.python.org/en/latest/specifications/declaring-project-metadata/
