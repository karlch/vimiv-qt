# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands and status modules using the api.

These should not be used anywhere else and are only imported to register the
corresponding objects.
"""

import os
from typing import List

from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QGuiApplication, QClipboard

from vimiv import api
from vimiv.utils import files, log, imagereader


_logger = log.module_logger(__name__)


###############################################################################
#                                  Commands                                   #
###############################################################################
@api.keybindings.register("<button-middle>", "enter thumbnail", mode=api.modes.LIBRARY)
@api.keybindings.register("<button-middle>", "enter thumbnail", mode=api.modes.IMAGE)
@api.keybindings.register("<button-right>", "enter library", mode=api.modes.THUMBNAIL)
@api.keybindings.register("<button-right>", "enter library", mode=api.modes.IMAGE)
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
    modeobj = api.modes.get_by_name(mode)
    if modeobj == api.modes.COMMAND:
        raise api.commands.CommandError(
            "Entering command mode is ambiguous, please use :command or :search"
        )
    modeobj.enter()


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


@api.keybindings.register("yi", "copy-image")
@api.keybindings.register("yI", "copy-image --primary")
@api.commands.register()
def copy_image(
    primary: bool = False,
    width: int = None,
    height: int = None,
    size: int = None,
    count: int = None,
) -> None:
    """Copy currently selected image to system clipboard.

    **syntax:** ``:copy-image [--primary] [--width=WIDTH] [--height=HEIGHT]
    [--size=SIZE]``

    optional arguments:
        * ``--primary``: Copy to primary selection.
        * ``--width``: Scale width to the specified value.
        * ``--height``: Scale height to the specified value.
        * ``--size``: Scale longer side to the specified value.

    **count:** Equivalent to the ``--size`` option
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    path = api.current_path()

    try:
        reader = imagereader.get_reader(path)
        pixmap = reader.get_pixmap()
    except ValueError as e:
        log.error(str(e))
        return

    if size or count:
        pix_size = pixmap.size()

        size = count if count is not None else size

        if pix_size.height() >= pix_size.width():
            _logger.debug(f"Copy image with size {size} restricting height")
            pixmap = pixmap.scaledToHeight(size)  # type: ignore[arg-type]
        else:
            _logger.debug(f"Copy image with size {size} restricting width")
            pixmap = pixmap.scaledToWidth(size)  # type: ignore[arg-type]

    elif width:
        _logger.debug(f"Copy image with width {width}")
        pixmap = pixmap.scaledToWidth(width)

    elif height:
        _logger.debug(f"Copy image with height {height}")
        pixmap = pixmap.scaledToHeight(height)

    clipboard.setPixmap(pixmap, mode=mode)


@api.commands.register()
def paste_name(primary: bool = True) -> None:
    """Paste path from clipboard to open command.

    **syntax:** ``:paste-name [--primary]``

    optional arguments:
        * ``--primary``: Paste from  primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    api.open_paths([clipboard.text(mode=mode)])


@api.commands.register(edit=True)
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
        ``:rename %f identifier`` would rename all images in the filelist to
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
    paths = api.settings.sort.image_order.sort(paths)
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


@api.commands.register(edit=True)
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


@api.commands.register()
def print_stdout(text: List[str], sep: str = "\n", end: str = "\n") -> None:
    """Print text to the terminal.

    **syntax:** ``:print-stdout text [--sep] [--end]``

    positional arguments:
        * ``text``: List of strings to concatenate and print

    optional arguments:
        * ``--sep``: String inserted between list element, default is new line.
        * ``--end``: String appended after last element, default is new line.
    """
    print(*text, sep=sep, end=end)


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


@api.status.module("{read-only}")
def read_only() -> str:
    """Print ``[RO]`` if read_only is true."""
    if api.settings.read_only:
        return " [RO]"
    return ""
