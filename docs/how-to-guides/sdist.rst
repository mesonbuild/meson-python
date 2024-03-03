.. SPDX-FileCopyrightText: 2024 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _sdist:

******************************
Creating a source distribution
******************************

A source distribution for the project can be created executing

.. code-block:: console

   $ python -m build --sdist .

in the project root folder. This will create a ``.tar.gz`` archive in the
``dist`` folder in the project root folder. This archive contains the full
contents of the latest commit in revision control with all revision control
metadata removed. Uncommitted modifications and files unknown to the revision
control system are not included.

The source distribution archive is created by adding the required metadata
files to the archive obtained by executing the ``meson dist --no-tests
--allow-dirty`` command. To generate a source distribution, ``meson-python``
must successfully configure the Meson project by running the ``meson setup``
command. Additional arguments can be passed to ``meson dist`` to alter its
behavior. Refer to the relevant `Meson documentation`__ and to the
:ref:`how-to-guides-meson-args` guide for details.

The ``meson dist`` command uses the archival tool of the underlying revision
control system for creating the archive. This implies that a source
distribution can only be created for a project versioned in a revision control
system. Meson supports the Git and Mercurial revision control systems.

Files can be excluded from the source distribution via the relevant mechanism
provided by the revision control system. When using Git as a revision control
system, it is possible to exclude files from the source distribution setting
the ``export-ignore`` attribute. For example, adding a ``.gitattributes``
files containing

.. code-block:: none

   dev/** export-ignore

would result in the ``dev`` folder to be excluded from the source
distribution. Refer to the ``git archive`` documentation__ for
details. Another mechanism to alter the content of the source distribution is
offered by dist scripts. Refer to the relevant `Meson documentation`__ for
details.

__ https://mesonbuild.com/Creating-releases.html
__ https://git-scm.com/docs/git-archive#ATTRIBUTES
__ https://mesonbuild.com/Reference-manual_builtin_meson.html#mesonadd_dist_script
