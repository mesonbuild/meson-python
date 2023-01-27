.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _reference-quirks:

******
Quirks
******

.. todo::

   - Document requirements on how ``import('python').find_installation()`` is
     called (see `#233`_)
   - Document that Meson, and thus meson-python, require MSVC compilers to be
     found in ``$PATH`` on Windows (see `#224`_)


.. _reference-quirks-mixing-purelib-and-platlib:

Mixing ``purelib`` and ``platlib``
==================================


.. todo::

   - Explain in which cases, and how this can cause issues
   - Explain how to fix (specifying ``pure`` in the necessary targets)
   - Present changing ``pure`` globally as an option (depending on the use-case)


.. _#233: https://github.com/mesonbuild/meson-python/issues/233
.. _#224: https://github.com/mesonbuild/meson-python/issues/224
