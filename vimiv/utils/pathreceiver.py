# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Functions to get the current path and pathlist."""

from vimiv.imutils import imstorage
from vimiv.gui import library, thumbnail
from vimiv.modes import modehandler, Modes


def current(mode=None):
    """Get the currently selected path.

    Args:
        mode: Force getting the currently selected path of a specific mode.
    Return:
        The currently selected path as abspath.
    """
    mode = mode if mode else modehandler.current()
    if mode == Modes.LIBRARY:
        return library.instance().current()
    if mode in [Modes.IMAGE, Modes.MANIPULATE]:
        return imstorage.current()
    if mode == Modes.THUMBNAIL:
        return thumbnail.instance().abspath()
    return ""


def pathlist(mode=None):
    """Get the list of all currently open paths.

    Args:
        mode: Force getting the pathlist of a specific mode.
    Return:
        The list of currently open paths.
    """
    mode = mode if mode else modehandler.current()
    if mode == Modes.LIBRARY:
        return library.instance().pathlist()
    if mode in [Modes.IMAGE, Modes.THUMBNAIL]:
        return imstorage.pathlist()
    return []
