.. SPDX-FileCopyrightText: 2026 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _building-a-package:

******************
Building a package
******************

What build isolation covers
===========================

A frontend such as ``python -m build`` reads ``[build-system]`` from
``pyproject.toml``. With isolation enabled, it installs the Python build
requirements into a temporary environment before invoking the
``mesonpy`` backend. The backend invokes Meson to configure, compile and
install the files that go in the wheel.

A virtual environment you activate before running the frontend controls
which frontend and interpreter you use. It does not replace the temporary
build environment. If you pass ``--no-isolation`` to ``python -m build``,
activate the intended environment and install all the project's build
requirements there first. This can be useful when testing a specific
version of a build dependency. Neither mode installs system requirements
such as a C compiler, SDK or system libraries.

See the :ref:`build configuration settings <how-to-guides-config-settings>` for
passing options to Meson from the frontend.

When a wheel is ready to distribute
===================================

A native wheel built for local use can still depend on shared libraries
installed on your machine. Trying it in a fresh Python virtual environment
on the build machine does not remove those system libraries. A wheel tag
describes compatibility, and does not check the native dependencies.

For a release, decide what platforms, architectures and Python versions you
support. Build in environments that target them, for example with
`cibuildwheel <https://cibuildwheel.pypa.io/>`_. Use the platform's wheel
inspection and repair tool to check dependencies and, where permitted,
bundle redistributable libraries. Common choices are
`auditwheel <https://github.com/pypa/auditwheel>`_ on Linux,
`delocate <https://github.com/matthew-brett/delocate>`_ on macOS and
`delvewheel <https://github.com/adang1345/delvewheel>`_ on Windows.
Consult your dependencies' licenses before bundling them.
See :ref:`internal-shared-libraries` for how meson-python handles libraries
built as part of the project.

Install the resulting wheel, and exercise the import or command that loads
the native code on each supported target without relying on a developer's
preinstalled libraries. For background, see
`Building and installing or uploading artifacts
<https://pypackaging-native.github.io/meta-topics/build_steps_conceptual/#building-and-installing-or-uploading-artifacts>`_.
