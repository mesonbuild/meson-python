.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-debug-builds:

******************
Using debug builds
******************

For development work on native code in your Python package, you may want to use
a debug build. To do so, we need to pass the ``-Dbuildtype=debug`` option, which is
equivalent to ``-Ddebug=true -Doptimization=0``, to ``meson setup``. In addition,
it is likely most useful to set up an editable build with a fixed build
directory. That way, the shared libraries in the installed debug build will
contain correct paths, rather than paths pointing to a temporary build
directory which ``meson-python`` will otherwise use. IDEs and other tools will
then be able to show correct file locations and line numbers during debugging.

We can do all that with the following ``pip`` invocation:

.. code-block:: console

    $ pip install -e . --no-build-isolation \
        -Csetup-args=-Dbuildtype=debug \
        -Cbuilddir=build-dbg

This debug build of your package will work with either a regular or debug build
of your Python interpreter. A debug Python interpreter isn't necessary, but may
be useful. It can be built from source, or you may be able to get it from your
package manager of choice (typically under a package name like ``python-dbg``).
Note that using a debug Python interpreter does not yield a debug build of your
own package - you must use ``-Dbuildtype=debug`` or an equivalent flag for that.

.. warning::

    Inside a Conda environment, environment variables like ``CFLAGS`` and
    ``CXXFLAGS`` are usually set when the environment is activated. These
    environment variables contain optimization flags like ``-O2``, which will
    override the optimization level implied by ``-Dbuildtype=debug``. In order
    to avoid this, unset these variables:

    .. code-block:: console

        $ unset CFLAGS
        $ unset CXXFLAGS

Finally, note changing the buildtype from its default value of ``release`` to
``debug`` will also cause ``meson-python`` to enable (or better, not disable)
assertions by not defining the ``NDEBUG`` macro (see ``b_ndebug`` under
:ref:`explanations-default-options`).
