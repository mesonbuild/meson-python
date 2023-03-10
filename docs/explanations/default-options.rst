.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _explanations-default-options:

*********************
Default build options
*********************

Meson offers many `built-in options <https://mesonbuild.com/Builtin-options.html>`__,
and in the vast majority of cases those have good defaults. There are a couple
of cases however where ``meson-python`` either needs to or chooses to override
those with its own defaults. To view what those are for the version of
``meson-python`` you have installed, look at the *User defined options* section
of the output during the configure stage of the build (e.g., by running
``python -m build --wheel``). This will look something like:

.. code-block:: text

    User defined options
      Native files     : /home/username/code/project/.mesonpy-native-file.ini
      debug            : false
      optimization     : 2
      prefix           : /home/username/mambaforge/envs/project-dev
      python.platlibdir: /home/username/mambaforge/envs/project-dev/lib/python3.10/site-packages
      python.purelibdir: /home/username/mambaforge/envs/project-dev/lib/python3.10/site-packages
      b_ndebug         : if-release

Let's go through each option and why they are used:

- meson-python uses a native file, written to the build dir and named
  ``mesonpy-native-file.ini``, in order to point Meson at the correct
  ``python`` interpreter to use (the same one for which ``meson-python`` was
  installed). This is necessary, because Meson may otherwise look for the first
  Python interpreter on the PATH (usually the same one, but not always the
  case). Users may use ``--native-file`` to pass a second native file to Meson;
  Meson will merge contents of both native file, so as long as the
  user-provided file does not try to pass a different path for the ``python``
  binary, this will work without a conflict.
- The ``prefix`` and ``platlibdir``/``purelibdir`` options also point Meson at
  that same interpreter and the environment in which it is installed.
- The ``debug``, ``optimization`` and ``b_ndebug`` options are overridden,
  because Meson defaults to values that are appropriate for development, while
  the main purpose of meson-python is to build release artifacts.

It is possible to override these defaults, either permanently in your project
or at build time. For example, to build a wheel with debug symbols, use:

.. code-block:: console

   $ python -m build -Csetup-args=-Ddebug=true

And to override all debug and optimization settings permanently, add this to
your ``pyproject.toml`` file:

.. code-block:: toml

   [tool.meson-python.args]
   setup = ['-Ddebug=true', '-Doptimization=0', '-Db_ndebug=false']

For more details on overriding build options at build time see the
:ref:`reference-config-settings` page, and in ``pyproject.toml`` see the
:ref:`reference-pyproject-settings` page.
