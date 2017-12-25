# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Copy to and paste from system clipboard."""

import os

from PyQt5.QtGui import QGuiApplication

from vimiv import app
from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.modes import modehandler
from vimiv.utils import impaths, objreg


@keybindings.add("ya", "copy-name --abspath")
@keybindings.add("yy", "copy-name")
@commands.argument("abspath", optional=True, action="store_true")
@commands.register(hide=True)
def copy_name(abspath):
    """Copy name of current path to system clipboard.

    Args:
        abspath: Copy absolute path instead of basename.
    """
    clipboard = QGuiApplication.clipboard()
    basename = _get_path_name()
    name = os.path.abspath(basename) if abspath else basename
    clipboard.setText(name)


def _get_path_name():
    mode = modehandler.current().lower()
    if mode == "image":
        return os.path.basename(impaths.current())
    library = objreg.get("library")
    return library.current()


@keybindings.add("Pp", "paste-name")
@commands.register(hide=True)
def paste_name():
    """Paste path from clipboard to open command."""
    clipboard = QGuiApplication.clipboard()
    app.open(clipboard.text())
