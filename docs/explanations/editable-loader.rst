.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _explanations-editable-loader:

How editable installs resolve package files
===========================================

A regular wheel contains the files that Python imports. An editable
wheel instead installs a loader that knows where the Meson build
directory is. When Python first asks the loader for a module in the
editable package, the loader runs the build command and reads Meson's
install plan. The plan maps each install location to a file in the
source tree or the build directory.

A pure Python module can therefore be loaded from the source tree,
while a native extension in the same package is loaded from the build
directory. The paths that Python sees do not have to share a parent
directory. That is why package data should be read through
``importlib.resources`` instead of assuming that it sits next to
``__file__``.

The loader reuses the result during the process. Start a new Python
process after editing compiled source to trigger a new build on import.
Changes to package metadata, such as entry points and dependencies,
still require reinstalling the editable package.

For setup and troubleshooting, see :ref:`how-to-guides-editable-installs`.
