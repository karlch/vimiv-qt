# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Copy to and paste from system clipboard."""

import os

from PyQt5.QtGui import QGuiApplication, QClipboard

from vimiv import app
from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.imutils import imstorage
from vimiv.modes import modehandler
from vimiv.utils import objreg


@keybindings.add("yA", "copy-name --abspath --primary")
@keybindings.add("yY", "copy-name --primary")
@keybindings.add("ya", "copy-name --abspath")
@keybindings.add("yy", "copy-name")
@commands.argument("primary", optional=True, action="store_true")
@commands.argument("abspath", optional=True, action="store_true")
@commands.register(hide=True)
def copy_name(abspath, primary):
    """Copy name of current path to system clipboard.

    Args:
        abspath: Copy absolute path instead of basename.
    """
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    basename = _get_path_name()
    name = os.path.abspath(basename) if abspath else basename
    clipboard.setText(name, mode=mode)


def _get_path_name():
    """Return base name of currently selected path."""
    # TODO move this to another module?
    mode = modehandler.current().lower()
    if mode == "image":
        return os.path.basename(imstorage.current())
    library = objreg.get("library")
    return library.current()


@keybindings.add("PP", "paste-name --primary")
@keybindings.add("Pp", "paste-name")
@commands.argument("primary", optional=True, action="store_true")
@commands.register(hide=True)
def paste_name(primary):
    """Paste path from clipboard to open command."""
    clipboard = QGuiApplication.clipboard()
    mode = QClipboard.Selection if primary else QClipboard.Clipboard
    app.open(clipboard.text(mode=mode))
