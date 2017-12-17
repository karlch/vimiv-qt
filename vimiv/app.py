# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Main application class using QApplication."""

import os

from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv.config import keybindings
from vimiv.commands import commands
from vimiv.utils import objreg, impaths, libpaths, files, modehandler


class Application(QApplication):
    """Main application class."""

    @objreg.register("app")
    def __init__(self):
        """Initialize the main Qt application."""
        super().__init__([vimiv.__name__])  # Only pass program name to Qt

    @keybindings.add("q", "quit")
    @commands.register(instance="app")
    def quit(self):
        """Quit the QApplication and therefore exit."""
        super().quit()


# We want to use the name open here as it is the best name for the command
@commands.argument("no-select-mode", optional=True, action="store_true")
@commands.argument("paths")
@commands.register()
def open(paths, no_select_mode=False):  # pylint: disable=redefined-builtin
    """Open a list of paths.

    If the paths contain images, these are opened in image mode. Otherwise if
    the paths contain directories, the first directory is opened in the
    library.

    Args:
        paths: List of paths to open. A single path string is converted to a
            list containing only this path.
    """
    if isinstance(paths, str):
        paths = [paths]
    images, directories = files.get_supported(paths)
    mode = ""
    if images:
        os.chdir(os.path.dirname(os.path.abspath(images[0])))
        impaths.load(images)
        mode = "image"
    elif directories:
        libpaths.load(directories[0])
        mode = "library"
    if mode and not no_select_mode:
        modehandler.enter(mode)
