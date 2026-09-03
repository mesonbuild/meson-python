.. SPDX-FileCopyrightText: 2023 The meson-python developers
..
.. SPDX-License-Identifier: MIT

Release Process
===============

Releases are published as git tags, signed with either an SSH or a PGP key
belonging to a maintainer. The signing key must be registered on GitHub so that
GitHub shows the tag as verified.

You may release the project by following these steps:

#. Release to the Git repository on GitHub:

   #. Create the release commit

      #. Bump the versions in ``pyproject.toml`` and in ``mesonpy/__init__.py``.
      #. Create ``CHANGELOG.rst`` section for the new release and fill it.
      #. The commit message should read: ``REL: set version to X.Y.Z``

   #. Create a signed tag for the release:

      .. code-block:: console

         $ git tag -s X.Y.Z

      This signs with your PGP key by default. To sign with an SSH key instead,
      configure git once beforehand:

      .. code-block:: console

         $ git config --global gpg.format ssh
         $ git config --global user.signingkey ~/.ssh/id_ed25519.pub

      The SSH signing key must be registered on
      GitHub as a Signing Key for the tag to show as verified.

      The tag title should follow the ``meson-python X.Y.Z`` format, and the
      tag body should be a plain text version of the change-log for the current
      release.

   #. Push the tag to the repository:

      .. code-block:: console

         $ git push --tags

#. Release to PyPI is done via trusted publishing, triggering on the tag.
