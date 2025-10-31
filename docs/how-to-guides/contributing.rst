.. SPDX-FileCopyrightText: 2021 The meson-python developers
..
.. SPDX-License-Identifier: MIT

.. _how-to-guides-contributing:

Contributing
============

Thank you for your interest in contributing.  ``meson-python`` development is
hosted on GitHub_ and uses the ubiquitous pull-request based workflow.  The
usual Python development practices apply.  Python source code should adhere to
the `PEP 8`_ code style with a maximum line length of 127 characters.  Single
quotes are used as string delimiters.  Python code uses type annotations
verified via Mypy_ and is kept clean linting it with Ruff_.

``meson-python`` focus is producing Python wheels containing extension modules
and thus running its test suite requires C and C++ compilers, and CMake. The
``patchelf`` utility is required on Linux. These are best installed via the
system package manager.

The documentation is written in reST format and the published version is
generated with Sphinx_.

To work on the code:

1. Fork the repository.

2. Set up the development environment by creating a virtual environment and
   installing the necessary dependencies for development and testing:

   .. code-block:: console

      $ uv venv
      $ source .venv/bin/activate
      $ uv pip install meson ninja pyproject-metadata
      $ uv pip install --no-build-isolation --editable .
      $ uv pip install --group test
      $ uv pip install ruff mypy

3. Create your branch from the ``main`` branch.

4. Hack away. Add tests as necessary.

5. Run the linter, the type checker, and the test suite:

   .. code-block:: console

      $ ruff check
      $ mypy
      $ pytest

6. Organize your changes in logical commits with clear, concise, and well
   formatted commit messages describing the motivation for the change. Commit
   messages should be organized in a subject line, describing the commit
   briefly, followed by a blank line, and more test if needed. Lines should be
   word wrapped at 72 characters.

   The subject line should start with a capitalized acronym indicating the
   nature of the commit, followed by a colon. Used acronyms include: "BUG" for
   bug fixes, "ENH" for new features and other enhancements, "TST" for
   addition or modification of tests, "MAINT" for maintenance commits,
   typically refactoring, typo or code style fixes, "DOC" for documentation,
   "CI" for changes to the continuous integration setup.

To work on the documentation:

1. Install the required tools:

   .. code-block:: console

      $ uv pip install --group docs

2. Generate and inspect the HTML documentation:

   .. code-block:: console

      $ python -m sphinx docs html
      $ open html/index.html


.. _GitHub: https://github.com/meson/meson-python/
.. _Mypy: https://mypy.readthedocs.io
.. _PEP 8: https://www.python.org/dev/peps/pep-0008/
.. _Ruff: https://docs.astral.sh/ruff/
.. _Sphinx: https://www.sphinx-doc.org
