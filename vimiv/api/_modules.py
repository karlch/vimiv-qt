# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands and status modules using the api.

These should not be used anywhere else and are only imported to register the
corresponding objects.
"""

import os
from contextlib import suppress
from typing import List

from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QGuiApplication, QClipboard

import vimiv
from vimiv import api
from vimiv.utils import files, log


_logger = log.module_logger(__name__)


###############################################################################
#                                  Commands                                   #
###############################################################################
@api.keybindings.register("gm", "enter manipulate")
@api.keybindings.register("gt", "enter thumbnail")
@api.keybindings.register("gl", "enter library")
@api.keybindings.register("gi", "enter image")
@api.commands.register()
def enter(mode: str) -> None:
    """Enter another mode.

    **syntax:** ``:enter mode``

    positional arguments:
        * ``mode``: The mode to enter (image/library/thumbnail/manipulate).
    """
    api.modes.get_by_name(mode).enter()


@api.keybindings.register("tm", "toggle manipulate")
@api.keybindings.register("tt", "toggle thumbnail")
@api.keybindings.register("tl", "toggle library")
@api.commands.register()
def toggle(mode: str) -> None:
    """Toggle one mode.

    **syntax:** ``:toggle mode``.

    If the mode is currently visible, leave it. Otherwise enter it.

    positional arguments:
        * ``mode``: The mode to toggle (image/library/thumbnail/manipulate).
    """
    api.modes.get_by_name(mode).toggle()


@api.keybindings.register("yA", "copy-name --abspath --primary")
@api.keybindings.register("yY", "copy-name --primary")
@api.keybindings.register("ya", "copy-name --abspath")
@api.keybindings.register("yy", "copy-name")
@api.commands.register()
def copy_name(abspath: bool = False, primary: bool = False) -> None:
    """Copy name of current path to system clipboard.

    **syntax:** ``:copy-name [--abspath] [--primary]``

    optional arguments:
        * ``--abspath``: Copy absolute path instead of basename.
        * ``--primary``: Copy to primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    path = api.current_path()
    name = path if abspath else os.path.basename(path)
    clipboard.setText(name, mode=mode)


@api.commands.register()
def paste_name(primary: bool = True) -> None:
    """Paste path from clipboard to open command.

    **syntax:** ``:paste-name [--primary]``

    optional arguments:
        * ``--primary``: Paste from  primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    api.open([clipboard.text(mode=mode)])


# We want to use the name help here as it is the best name for the command
@api.commands.register(mode=api.modes.MANIPULATE)
@api.commands.register()
def help(topic: str) -> None:  # pylint: disable=redefined-builtin
    """Show help on a command or setting.

    **syntax:** ``:help topic``

    positional arguments:
        * ``topic``: Either a valid :command or a valid setting name.

    .. hint:: For commands ``help :command`` is the same as ``command -h``.
    """
    topic = topic.lower().lstrip(":")
    if topic == "vimiv":
        log.info(
            "%s: %s\n\n"
            "Website: %s\n\n"
            "For an overview of keybindings, run :keybindings.\n"
            "To retrieve help on a command or setting run :help topic.",
            vimiv.__name__,
            vimiv.__description__,
            vimiv.__url__,
        )
        return
    with suppress(api.commands.CommandNotFound):
        command = api.commands.get(topic, mode=api.modes.current())
        # This raises an exception and leaves this command
        command(["-h"], "")
    with suppress(KeyError):
        setting = api.settings.get(topic)
        log.info(
            "%s: %s\n\nType: %s\nDefault: %s\nSuggestions: %s",
            setting.name,
            setting.desc,
            setting,
            setting.default,
            ", ".join(setting.suggestions()),
        )
        return
    raise api.commands.CommandError(f"Unknown topic '{topic}'")


@api.commands.register()
def rename(
    paths: List[str],
    base: str,
    start: int = 1,
    separator: str = "_",
    overwrite: bool = False,
    skip_image_check: bool = False,
) -> None:
    """Rename images with a common base.

    **syntax:** ``:rename path [path ...] base [--start=INDEX] [--separator=SEPARATOR]
    [--overwrite] [--skip-image-check]``

    Example::
        ``:rename * identifier`` would rename all images in the filelist to
        ``identifier_001``, ``identifier_002``, ..., ``identifier_NNN``.

    positional arguments:
        * ``paths``: The path(s) to rename.
        * ``base``: Base name to use for numbering.

    optional arguments:
        * ``--start``: Index to start numbering with. Default: 1.
        * ``--separator``: Separator between base and numbers. Default: '_'.
        * ``--overwrite``: Overwrite existing paths when renaming.
        * ``--skip-image-check``: Do not check if all renamed paths are images.
    """
    paths = [path for path in paths if files.is_image(path) or skip_image_check]
    if not paths:
        raise api.commands.CommandError("No paths to rename")
    marked = []
    for i, path in enumerate(paths, start=start):
        _, extension = os.path.splitext(path)
        dirname = os.path.dirname(path)
        basename = f"{base}{separator}{i:03d}{extension}"
        outfile = os.path.join(dirname, basename)
        if os.path.exists(outfile) and not overwrite:
            log.warning(
                "Outfile '%s' exists, skipping. To overwrite add '--overwrite'.",
                outfile,
            )
        else:
            _logger.debug("%s -> %s", path, outfile)
            os.rename(path, outfile)
            if path in api.mark.paths:  # Keep mark status of the renamed path
                marked.append(outfile)
    api.mark.mark(marked)


@api.commands.register()
def mark_rename(
    base: str, start: int = 1, overwrite: bool = False, separator: str = "_"
) -> None:
    """Rename marked images with a common base.

    **syntax:** ``:mark-rename base [--start=INDEX] [--separator=SEPARATOR]
    [--overwrite] [--skip-image-check]``

    Example::
        ``:mark-rename my_mark`` would rename all marked images to
        ``my_mark_001``, ``my_mark_002``, ..., ``my_mark_NNN``.

    positional arguments:
        * ``paths``: The path(s) to rename.
        * ``base``: Base name to use for numbering.

    optional arguments:
        * ``--start``: Index to start numbering with. Default: 1.
        * ``--separator``: Separator between base and numbers. Default: '_'.
        * ``--overwrite``: Overwrite existing paths when renaming.
        * ``--skip-image-check``: Do not check if all renamed paths are images.
    """
    rename(
        api.mark.paths,
        base,
        start=start,
        overwrite=overwrite,
        separator=separator,
        skip_image_check=True,
    )


###############################################################################
#                               Status Modules                                #
###############################################################################
@api.status.module("{mode}")
def active_name() -> str:
    """Current mode."""
    return api.modes.current().name.upper()


@api.status.module("{pwd}")
def pwd() -> str:
    """Current working directory."""
    wd = os.getcwd()
    if api.settings.statusbar.collapse_home.value:
        wd = wd.replace(os.path.expanduser("~"), "~")
    return wd


@api.status.module("{filesize}")
def filesize() -> str:
    """Size of the current image in bytes."""
    return files.get_size(api.current_path())


@api.status.module("{modified}")
def modified() -> str:
    """Modification date of the current image."""
    try:
        mtime = os.path.getmtime(api.current_path())
    except OSError:
        return "N/A"
    date_time = QDateTime.fromSecsSinceEpoch(int(mtime))
    return date_time.toString("yyyy-MM-dd HH:mm")
