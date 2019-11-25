# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""`Utilities to interact with the application`."""

import os
from typing import List, Iterable

from vimiv.utils import files

from . import (
    commands,
    completion,
    keybindings,
    modes,
    objreg,
    settings,
    signals,
    status,
    working_directory,
    _mark,
    _modules,
)

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


# We want to use the name open here as it is the best name for the command
@keybindings.register("o", "command --text='open '")
@commands.register()
def open(paths: Iterable[str]) -> None:  # pylint: disable=redefined-builtin
    """Open one or more paths.

    **syntax:** ``:open path [path ...]``

    If any path given is an image, all valid images are opened in image mode. Otherwise
    the first valid directory is opened. If both fails, an error is displayed.

    positional arguments:
        * ``paths``: The path(s) to open.
    """
    images, directories = files.supported(paths)
    if images:
        working_directory.handler.chdir(os.path.dirname(images[0]))
        signals.load_images.emit(images)
        modes.IMAGE.enter()
    elif directories:
        working_directory.handler.chdir(directories[0])
        modes.LIBRARY.enter()
    else:
        raise commands.CommandError("No valid paths")
