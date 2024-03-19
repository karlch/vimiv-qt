# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""`Utilities to interact with the application`."""

import os
from typing import List, Iterable, Callable, BinaryIO
from vimiv.qt.gui import QPixmap

from vimiv.utils import files, imagereader, imageheader

from vimiv.api import (
    commands,
    completion,
    keybindings,
    modes,
    objreg,
    prompt,
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
    return list(mode.pathlist)  # Ensure we create a copy


@keybindings.register("o", "command --text='open '")
@commands.register(name="open")
def open_paths(paths: Iterable[str], open_images: bool = False) -> None:
    """Open one or more paths.

    **syntax:** ``:open path [path ...]``

    If any path given is an image, all valid images are opened in image mode. Otherwise
    the first valid directory is opened. If both fails, an error is displayed.

    .. hint:: Passing a single directory therefore changes the directory in the library,
        think ``cd``.

    positional arguments:
        * ``paths``: The path(s) to open.

    optional arguments:
        * ``--open-images``: If True, open any images in a new directory automatically.
    """
    images, directories = files.supported(paths)
    if images:
        working_directory.handler.chdir(os.path.dirname(images[0]))
        signals.load_images.emit(images)
        modes.IMAGE.enter()
    elif directories:
        # This is always the library, admittedly a bit hacky to access like this
        modes.LIBRARY.widget.autoload = open_images  # type: ignore [attr-defined]
        working_directory.handler.chdir(directories[0])
        modes.LIBRARY.enter()
    else:
        raise commands.CommandError("No valid paths")


def add_external_format(
    file_format: str,
    test_func: imageheader.CheckFuncT,
    load_func: Callable[[str], QPixmap],
) -> None:
    """Add support for new fileformat.

    Args:
        file_format: String value of the file type
        test_func: Function returning True if load_func supports this type.
        load_func: Function to load a QPixmap from the passed path.
    """
    # Prioritize external formats over all default formats, to ensure that on signature
    # collision, the explicitly registered handler is used.
    imageheader.register(file_format, test_func, priority=True)
    imagereader.external_handler[file_format] = load_func
