# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Functions to get the current path and pathlist."""

from vimiv.modes import modehandler
from vimiv.utils import objreg


def current(mode=None):
    """Get the currently selected path.

    Args:
        mode: Force getting the currently selected path of a specific mode.
    Return:
        The currently selected path as abspath.
    """
    mode = mode if mode else modehandler.current()
    if mode == "library":
        return objreg.get("library").current()
    elif mode in ["image", "manipulate"]:
        return objreg.get("imstorage").current()
    elif mode == "thumbnail":
        return objreg.get("thumbnail").abspath()
    return ""


def pathlist(mode=None):
    """Get the list of all currently open paths.

    Args:
        mode: Force getting the pathlist of a specific mode.
    Return:
        The list of currently open paths.
    """
    mode = mode if mode else modehandler.current()
    if mode == "library":
        return objreg.get("library").pathlist()
    elif mode in ["image", "thumbnail"]:
        return objreg.get("imstorage").pathlist()
    return []
