# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Main application class using QApplication."""

import os

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv import api, utils


_logger = utils.log.module_logger(__name__)


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
        self.exit(0)

    @staticmethod
    def preexit(returncode):
        """Prepare exit by finalizing any running threads."""
        # Do not start any new threads
        utils.Pool.clear()
        # Wait for any running threads to exit safely
        _logger.debug("Waiting for any running threads...")
        utils.Pool.wait()
        _logger.debug("Exiting with returncode %d", returncode)

    def exit(self, returncode):
        """Exit the main application with returncode."""
        self.preexit(returncode)
        super().exit(returncode)

    @utils.asyncfunc()
    def _set_icon(self):
        """Set window icon of vimiv."""
        _logger.debug("Trying to retrieve icon from theme")
        icon = QIcon.fromTheme(vimiv.__name__)
        if icon.isNull():
            _logger.debug("Trying to retrieve icon from project directory")
            icon = self._icon_from_project_directory()
            if icon.isNull():
                utils.log.error("Failed loading icon")
                return
        self.setWindowIcon(icon)

    def _icon_from_project_directory(self):
        """Try to retrieve the icon from the icons folder.

        Useful if vimiv was not installed but is used from the git project.
        """
        icon = QIcon()
        file_dir = os.path.realpath(os.path.dirname(__file__))
        project_dir = os.path.join(file_dir, os.pardir)
        icon_dir = os.path.join(project_dir, "icons")
        for size in (16, 32, 64, 128, 256, 512):
            path = os.path.join(icon_dir, f"vimiv_{size}x{size}.png")
            pixmap = QPixmap(path)
            icon.addPixmap(pixmap)
        return icon
