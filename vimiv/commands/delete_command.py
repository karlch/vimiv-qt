# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands to move files to and restore files from the trash directory."""

import os
from typing import List

from vimiv import api
from vimiv.utils import files, log, trash_manager

_last_deleted: List[str] = []


@api.keybindings.register("x", "delete %")
@api.commands.register()
def delete(paths: List[str]) -> None:
    """Move one or more images to the trash directory.

    **syntax:** ``:delete path [path ...]``

    positional arguments:
        * ``paths``: The path(s) to the images to delete.

    .. note:: This only deletes images, not any other path(s).
    """
    _last_deleted.clear()
    images = [path for path in paths if files.is_image(path)]
    if not images:
        raise api.commands.CommandError("No images to delete")
    for filename in images:
        trash_filename = trash_manager.delete(filename)
        _last_deleted.append(os.path.basename(trash_filename))
    n_images = len(images)
    if n_images > 1:
        log.info("Deleted %d images", n_images)


@api.commands.register()
def undelete(basenames: List[str]) -> None:
    """Restore a file from the trash directory.

    **syntax:** ``:undelete [basename ...]``

    If no basename is given, the last deleted images in this session are restored.

    positional arguments:
        * ``basenames``: The basename(s) of the file in the trash directory.
    """
    basenames = basenames if basenames else _last_deleted
    for basename in basenames:
        try:
            trash_manager.undelete(basename)
        except FileNotFoundError as e:
            raise api.commands.CommandError(str(e))
