***************
Getting started
***************


Enabling the build backend
==========================

To use this build backend, you must specify it in your ``pyproject.toml`` file.

.. code-block:: toml

   [build-system]
   build-backend = 'mesonpy'
   requires = [
     'meson-python',
   ]


If you have any other build dependencies, you must also add them to the
``requires`` list.


Metadata
========


Specifying the project metadata
-------------------------------

We support specifying Python package metadata in the ``project`` table in
``pyproject.toml`` (:pep:`621`).

To do so, you just need to add a ``project`` section with the details you want
to specify (see :pep:`621` for the specification of the format).


.. code-block:: toml

   ...

   [project]
   name = 'orion'
   version = '1.2.3'
   description = 'The Orion constellation!'
   readme = 'README.md'
   license = { file = 'LICENSE' }
   keyword = ['constellation', 'stars', 'sky']
   authors = [
     { name = 'Filipe Laíns', email = 'lains@riseup.net' },
   ]
   classifiers = [
     'Development Status :: 4 - Beta',
     'Programming Language :: Python',
   ]

   requires-python = '>=3.7'
   dependencies = [
     'stars >= 1.0.0',
     'location < 3',
   ]

   [project.optional-dependencies]
   test = [
     'pytest >= 3',
     'telescope',
   ]

   [project.urls]
   homepage = 'https://constellations.example.com/orion'
   repository = 'https://constellations.example.com/orion/repo'
   documentation = 'https://constellations.example.com/orion/docs'
   changelog = 'https://constellations.example.com/orion/docs/changelog.html'


In case you want us to detect the version automatically from Meson, you can omit
the ``version`` field and add it to ``project.dynamic``.

.. code-block:: toml

   ...

   [project]
   name = 'orion'
   dynamic = [
     'version',
   ]
   ...


Automatic metadata
------------------

If ``project`` metadata table is not specified, ``meson-python`` will
fetch the project name and version from Meson. In which case, you
don't need to add anything else to your ``pyproject.toml`` file.


.. admonition:: Warning
   :class: warning

   This is not recommended. Please consider specifying the Python package metadata.
