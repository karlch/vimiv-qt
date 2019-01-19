# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Main application class using QApplication."""

import logging
import os

from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv import api
from vimiv.imutils.imsignals import imsignals
from vimiv.utils import files, working_directory


class Application(QApplication):
    """Main application class."""

    @api.objreg.register
    def __init__(self):
        """Initialize the main Qt application."""
        super().__init__([vimiv.__name__])  # Only pass program name to Qt
        self.setApplicationVersion(vimiv.__version__)
        self.setDesktopFileName(vimiv.__name__)
        self._set_icon()

    @api.keybindings.register("q", "quit")
    @api.commands.register()
    def quit(self):
        """Quit vimiv."""
        # Do not start any new threads
        QThreadPool.globalInstance().clear()
        # Wait for any running threads to exit safely
        QThreadPool.globalInstance().waitForDone()
        super().quit()

    def _set_icon(self):
        """Set window icon of vimiv."""
        icon = QIcon.fromTheme(vimiv.__name__)
        if icon is None:
            logging.error("Failed to load icon")
        else:
            self.setWindowIcon(icon)


# We want to use the name open here as it is the best name for the command
@api.keybindings.register("o", "command --text='open '")
@api.commands.register()
def open(path: str):  # pylint: disable=redefined-builtin
    """Open a path.

    **syntax:** ``:open path``

    If the path is an image, it is opened in image mode. If it is a directory,
    it is opened in the library. Other paths are not supported.

    positional arguments:
        * ``path``: The path to open.
    """
    assert isinstance(path, str), "Path must be given as string."
    if not open_paths([os.path.expanduser(path)]):
        raise api.commands.CommandError("Cannot open %s" % (path))


def open_paths(paths, select_mode=True):
    """Open a list of paths possibly switching to a new mode.

    Args:
        paths: List of paths to open.
        select_mode: If True, select mode according to paths given.
    Return:
        True on success.
    """
    paths = [os.path.abspath(path) for path in paths]
    images, directories = files.supported(paths)
    mode = api.modes.LIBRARY
    if images:
        working_directory.handler.chdir(os.path.dirname(images[0]))
        imsignals.open_new_images.emit(images, images[0])
        mode = api.modes.IMAGE
    elif directories:
        working_directory.handler.chdir(directories[0])
    else:
        return False  # No valid paths found
    if select_mode:
        api.modes.enter(mode)
    return True


def instance():
    return api.objreg.get(Application)
