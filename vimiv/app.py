# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Main application class using QApplication."""

import os

from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv.config import keybindings
from vimiv.commands import commands, cmdexc
from vimiv.imutils import imcommunicate
from vimiv.modes import modehandler
from vimiv.utils import objreg, libpaths, files


class Application(QApplication):
    """Main application class."""

    @objreg.register("app")
    def __init__(self):
        """Initialize the main Qt application."""
        super().__init__([vimiv.__name__])  # Only pass program name to Qt

    @keybindings.add("q", "quit")
    @commands.register(instance="app")
    def quit(self):
        """Quit vimiv."""
        super().quit()


# We want to use the name open here as it is the best name for the command
@keybindings.add("o", "command --text=open")
@commands.argument("path")
@commands.register()
def open(path):  # pylint: disable=redefined-builtin
    """Open a path.

    If the path is an image, it is opened in image mode. Otherwise if it is a
    directory, it is opened in the library.

    Args:
        path: The path as string.
    """
    assert isinstance(path, str), "Path must be given as string."
    if not open_paths([os.path.expanduser(path)]):
        raise cmdexc.CommandError("Cannot open %s" % (path))


def open_paths(paths, select_mode=True):
    """Open a list of paths possibly switching to a new mode.

    Args:
        paths: List of paths to open.
        select_mode: If True, select mode according to paths given.
    Return:
        True on success.
    """
    images, directories = files.get_supported(paths)
    mode = "library"
    if images:
        imcommunicate.signals.update_paths.emit(images, 0)
        mode = "image"
    elif directories:
        libpaths.load(directories[0])
    else:
        return False
    if select_mode:
        modehandler.enter(mode)
    return True
