# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Copy to and paste from system clipboard."""

import os

from PyQt5.QtGui import QGuiApplication, QClipboard

from vimiv import app
from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.imutils import imstorage
from vimiv.modes import modehandler
from vimiv.utils import objreg


def init():
    """Initialize clipboard commands."""
    # Currently does not do anything but the commands need to be registered by
    # an import. May become useful in the future.


@keybindings.add("yA", "copy-name --abspath --primary")
@keybindings.add("yY", "copy-name --primary")
@keybindings.add("ya", "copy-name --abspath")
@keybindings.add("yy", "copy-name")
@commands.argument("primary", optional=True, action="store_true")
@commands.argument("abspath", optional=True, action="store_true")
@commands.register()
def copy_name(abspath, primary):
    """Copy name of current path to system clipboard.

    Args:
        abspath: Copy absolute path instead of basename.
        primary: Copy to primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    basename = _get_path_name()
    name = os.path.abspath(basename) if abspath else basename
    clipboard.setText(name, mode=mode)


def _get_path_name():
    """Return base name of currently selected path."""
    # TODO move this to another module?
    mode = modehandler.current()
    if mode == "image":
        return os.path.basename(imstorage.current())
    library = objreg.get("library")
    return library.current()


@keybindings.add("PP", "paste-name --primary")
@keybindings.add("Pp", "paste-name")
@commands.argument("primary", optional=True, action="store_true")
@commands.register()
def paste_name(primary):
    """Paste path from clipboard to open command.

    Args:
        primary: Paste from primary selection.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    app.open(clipboard.text(mode=mode))
