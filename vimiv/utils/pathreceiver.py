# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Functions to get the current path and pathlist."""

from typing import List

from vimiv import api, imutils
from vimiv.gui import library, thumbnail


def current(mode: api.modes.Mode = None) -> str:
    """Get the currently selected path.

    Args:
        mode: Force getting the currently selected path of a specific mode.
    Return:
        The currently selected path as abspath.
    """
    mode = mode if mode else api.modes.current()
    if mode == api.modes.LIBRARY:
        return library.instance().current()
    if mode in [api.modes.IMAGE, api.modes.MANIPULATE]:
        return imutils.current()
    if mode == api.modes.THUMBNAIL:
        return thumbnail.instance().abspath()
    return ""


def pathlist(mode: api.modes.Mode = None) -> List[str]:
    """Get the list of all currently open paths.

    Args:
        mode: Force getting the pathlist of a specific mode.
    Return:
        The list of currently open paths.
    """
    mode = mode if mode else api.modes.current()
    if mode == api.modes.LIBRARY:
        return library.instance().pathlist()
    if mode in [api.modes.IMAGE, api.modes.THUMBNAIL]:
        return imutils.pathlist()
    return []
