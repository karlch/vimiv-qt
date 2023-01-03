# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands to move files to and restore files from the trash directory."""

import os
from typing import List

from vimiv import api
from vimiv.utils import files, log, trash_manager, quotedjoin

_last_deleted: List[str] = []


@api.keybindings.register("x", "delete %")
@api.commands.register(edit=True)
def delete(paths: List[str], ask: bool = False) -> None:
    """Move one or more images to the trash directory.

    **syntax:** ``:delete path [path ...]``

    positional arguments:
        * ``paths``: The path(s) to the images to delete.

    optional arguments:
        * ``--ask``: Prompt for confirmation before deleting the images.

    .. note:: This only deletes images, not any other path(s).
    """
    if ask and not api.prompt.ask_question(
        title="delete", body=f"delete {quotedjoin(paths)}?"
    ):
        return
    _last_deleted.clear()
    images = [path for path in paths if files.is_image(path)]
    if not images:
        raise api.commands.CommandError("No images to delete")
    failed_images = []
    for filename in images:
        try:
            trash_filename = trash_manager.delete(filename)
            _last_deleted.append(os.path.basename(trash_filename))
        except OSError:
            failed_images.append(filename)

    n_fail = len(failed_images)
    n_success = len(images) - n_fail
    fail_msg = f"Failed to delete {', '.join(failed_images)}" if n_fail > 0 else ""
    succ_msg = f"Deleted {n_success} images" if n_success > 0 else ""

    if fail_msg:
        log.warning(f"{succ_msg + ' but ' if succ_msg else ''}{fail_msg}")
    elif succ_msg:
        log.info(succ_msg)


@api.commands.register(edit=True)
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
