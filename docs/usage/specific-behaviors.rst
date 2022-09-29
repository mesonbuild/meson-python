******************
Specific Behaviors
******************

This page documents how our backend handles certain situations.


``MACOSX_DEPLOYMENT_TARGET``
============================


The target macOS version can by changed by setting the
``MACOSX_DEPLOYMENT_TARGET`` environment variable.

If ``MACOSX_DEPLOYMENT_TARGET`` is set, we will use the selected version for the
wheel tag, otherwise ``platform.mac_ver()`` (i.e., the current macOS version on
the build machine) will be used instead.
