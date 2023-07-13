.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _explanations-internal-dependencies:

***************************************
How do we handle internal dependencies?
***************************************


.. todo::

   - Explain why bundle internal dependencies
   - Explain how we bundle internal dependencies

     - Explain how we patch the ``RPATH``

   - Mention our limitation regarding executables with internal dependencies

     - Link to the relevant :ref:`reference-limitations` section

   - Explain how to work around it (using a static library)

     - Mention how the ``pyproject.toml`` settings can be used to only enable
       the workaround on meson-python builds (by adding a custom Meson option
       and enabling it on meson-python builds)

         - Link to :ref:`reference-pyproject-settings`
