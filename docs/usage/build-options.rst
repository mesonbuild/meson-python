*************
Build options
*************

``builddir``
============

The ``builddir`` option allows the user to specify the build directory to use
for the Meson project. It takes the target path as an argument. If the path
exists, it will be used, if not, it will be created.


Example
-------

.. code-block:: bash

   $ python -m build -Cbuilddir=build
   # The `build` directory will be created and used to build the project.
   ...
   $ python -m build -Cbuilddir=build
   # The `build` directory, which already exists, will be re-used, speeding up the build a little.
   ...
