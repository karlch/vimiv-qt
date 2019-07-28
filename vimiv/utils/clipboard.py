# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Copy to and paste from system clipboard."""

import os

from PyQt5.QtGui import QGuiApplication, QClipboard

from vimiv import app, api


def init() -> None:
    """Initialize clipboard commands."""
    # Currently does not do anything but the commands need to be registered by
    # an import. May become useful in the future.


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
    app.open([clipboard.text(mode=mode)])
