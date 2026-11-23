.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

*********************
Bundling executables
*********************

Use Meson's ``executable()`` with ``install: true`` to include a native command
in a wheel. For example, put this in ``meson.build``:

.. code-block:: meson

   project('hello-bin', 'c', version: '0.1.0')
   executable('hello-meson', 'hello.c', install: true)

Add a ``hello.c`` source file:

.. code-block:: c

   #include <stdio.h>
   int main(void) {
       puts("Hello from Meson");
       return 0;
   }

Use the meson-python backend in ``pyproject.toml``:

.. code-block:: toml

   [build-system]
   requires = ['meson-python', 'ninja']
   build-backend = 'mesonpy'

Build a wheel, for example with ``uv build --wheel``. The default Meson install
directory for the executable is ``bindir``. The wheel has an entry under
``hello_bin-0.1.0.data/scripts/``, and a wheel installer places it in the target
environment's scripts directory. In an activated virtual environment,
``hello-meson`` can then run from the shell. A compiled executable makes the
wheel specific to the platform.

If the executable links to a library built by the project, prefer static
linking when practical. Installers move the executable out of
``.data/scripts/``. A loader path that works relative to the archive layout
might not reach a bundled shared library after installation. Test the command
from an installed wheel on each target platform if it depends on shared libraries.
