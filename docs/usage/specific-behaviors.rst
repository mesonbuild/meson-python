******************
Specific Behaviors
******************

This page documents how our backend handles certain situations.


``MACOSX_DEPLOYMENT_TARGET``
============================


.. note::

   macOS versioning changed from macOS 11 onwards. For macOS 10.x, the
   versioning scheme is ``10.major.minor``. From macOS 11, it is
   ``major.minor.bugfix``. Wheel tags and deployment targets are currently
   designed to be for major versions only. Examples of the platform part
   of tags that are currently accepted by, e.g., ``pip`` are:
   ``macosx_10_9``, ``macosx_10_13``, ``macosx_11_0``, ``macosx_12_0``.

The target macOS version can be changed by setting the
``MACOSX_DEPLOYMENT_TARGET`` environment variable.

If ``MACOSX_DEPLOYMENT_TARGET`` is set, we will use the selected version for the
wheel tag. Please use major versions only, so ``10.13``, ``11``, ``12``.
If ``MACOSX_DEPLOYMENT_TARGET`` is not set, the current macOS major version on
the build machine will be used instead (derived from ``platform.mac_ver()``).

Note that another way of specifying the target macOS platform is to explicitly
use ``-mmacosx-version-min`` compile and link flags when invoking Clang or GCC.
It is not possible for ``meson-python`` to detect this though, so it will not
set the wheel tag to that flag automatically.
