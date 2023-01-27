.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-executable-with-internal-dependencies:

*************************************
Executable with internal dependencies
*************************************


.. todo::

   - Mention our limitation regarding executables with internal dependencies

     - Link to the relevant :ref:`reference-limitations` section

   - Explain how to work around it (using a static library)

     - Mention how the ``pyproject.toml`` settings can be used to only enable
       the workaround on meson-python builds (by adding a custom Meson option
       and enabling it on meson-python builds)

         - Link to :ref:`reference-pyproject-settings`
