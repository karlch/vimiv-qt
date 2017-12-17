# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Main application class using QApplication."""

import logging
import os

from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv.config import keybindings
from vimiv.commands import commands
from vimiv.utils import objreg, impaths, libpaths, modehandler, files


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
@commands.argument("paths")
@commands.register()
def open(paths):  # pylint: disable=redefined-builtin
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
    if images:
        if directories:
            logging.warning(
                "Images and directories given as PATHS. Using images.")
        os.chdir(os.path.dirname(os.path.abspath(images[0])))
        impaths.load(images)
        modehandler.enter("image")
    elif directories:
        if len(directories) > 1:
            logging.warning("Multiple directories given as PATHS. "
                            "Using %s.", directories[0])
        libpaths.load(directories[0])
        modehandler.enter("library")
