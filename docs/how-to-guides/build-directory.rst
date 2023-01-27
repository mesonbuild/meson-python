.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-build-directory:

*******************************
Use a permanent build directory
*******************************


.. todo::

   - Explain why you'd want to use the ``builddir`` option
     - Mention it works properly when using ``--cross-file`` (eg. https://github.com/scipy/scipy/blob/1c836efe5ff37ffa4490756269b060a464690e62/.github/workflows/wheels.yml#L180-L188)
   - Explain how ``builddir`` works
   - Warn that user-configured build directories are "use at your own risk"
   - Warn that ``meson-python`` version mismatches in the build directory can
     cause trouble
