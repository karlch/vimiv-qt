# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities to interact with the application`."""

from typing import List

from . import (
    commands,
    completion,
    keybindings,
    modes,
    objreg,
    settings,
    status,
    _mark,
    _modules,
)

# This is required to happen after importing locally due to cyclic import issues
from vimiv import imutils, utils  # pylint: disable=wrong-import-order

mark = _mark.Mark()


def current_path(mode: modes.Mode = None) -> str:
    """Get the currently selected path.

    Args:
        mode: Force getting the currently selected path of a specific mode.
    Returns:
        The currently selected path as abspath.
    """
    mode = mode if mode else modes.current()
    return mode.current_path


def pathlist(mode: modes.Mode = None) -> List[str]:
    """Get the list of all currently open paths.

    Args:
        mode: Force getting the pathlist of a specific mode.
    Returns:
        The list of currently open paths.
    """
    mode = mode if mode else modes.current()
    return mode.pathlist
