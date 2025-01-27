.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

Release Process
===============

All releases are PGP signed with one of the keys listed in ``docs/about.rst``.
Before releasing please make sure your PGP key is listed there, and preferably
signed by one of the other key holders.

If your key is not signed by one of the other key holders, please make sure
that the PR that added your key to ``docs/about.rst`` was approved by at least
one other maintainer.

After that is done, you may release the project by following these steps:

#. Release to the Git repository on GitHub:

   #. Create the release commit

      #. Bump the versions in ``pyproject.toml`` and in ``mesonpy/__init__.py``.
      #. Create ``CHANGELOG.rst`` section for the new release and fill it.
      #. The commit message should read: ``REL: set version to X.Y.Z``

   #. Create a GPG-signed tag for the release:

      .. code-block:: console

         $ git tag -s X.Y.Z

      The tag title should follow the ``meson-python X.Y.Z`` format, and the
      tag body should be a plain text version of the change-log for the current
      release.

   #. Push the commit and tag to the repository:

      .. code-block:: console

         $ git push
         $ git push --tags

#. Release to PyPI:

   #. Build the Python artifacts:

      .. code-block:: console

         $ python -m build

   #. Push the artifacts to PyPI:

      .. code-block:: console

         $ twine upload dist/*

      There is no need to GPG-sign the artifacts: PyPI no longer
      supports uploading GPG signatures.
