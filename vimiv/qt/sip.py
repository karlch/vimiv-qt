# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

# pylint: disable=missing-module-docstring,wildcard-import,unused-wildcard-import

from vimiv import qt


if qt.WRAPPER == qt.WRAPPERS.PyQt5:
    # Different location under PyQt < 5.11
    try:
        from PyQt5.sip import *
    except ImportError:  # pragma: no cover  # Covered in a different tox env during CI
        from sip import *  # type: ignore
