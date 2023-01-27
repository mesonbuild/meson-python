.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _contributing-documentation:

*************
Documentation
*************

Our documentation is built on sphinx_, is written using reStructuredText_, and
follows the Diátaxis_ framework.

To automatically re-build the documentation and serve it on an web server, you
can pass the ``serve`` argument to the ``docs`` nox_ task.


.. code-block:: console

   $ nox -s docs -- serve


When using this argument, the task will watch the documentation source files,
and every time you edit something, it will automatically re-build the
documentation and make it available on the provided web server.


.. todo::

   Elaborate more with tips on how to write.


.. _sphinx: https://www.sphinx-doc.org
.. _reStructuredText: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _Diátaxis: https://diataxis.fr/
.. _nox: https://github.com/wntrblm/nox
