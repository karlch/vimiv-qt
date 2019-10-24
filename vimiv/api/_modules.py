# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Commands and status modules using the api.

These should not be used anywhere else and are only imported to register the
corresponding objects.
"""

import datetime
import os

from PyQt5.QtGui import QGuiApplication, QClipboard

from vimiv import api
from vimiv.utils import files


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
    d = datetime.datetime.fromtimestamp(mtime)
    return d.strftime("%y-%m-%d %H:%M")
