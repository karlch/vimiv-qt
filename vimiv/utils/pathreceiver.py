# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Functions to get the current path and pathlist."""

from vimiv.modes import modehandler
from vimiv.utils import objreg


def current():
    """Get the currently selected path."""
    mode = modehandler.current()
    if mode == "library":
        return objreg.get("library").current()
    elif mode in ["image", "thumbnail"]:
        return objreg.get("imstorage").current()
    else:
        return ""
