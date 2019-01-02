# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to take care of the current working directory.

The handler stores the current working directory and provides a method to
change it. In addition the directory is monitored using QFileSystemWatcher.

Module Attributes:
    handler: The initialized WorkingDirectoryHandler object.
"""

import logging
import os

from PyQt5.QtCore import pyqtSignal, pyqtSlot, QFileSystemWatcher

from vimiv.config import settings


class WorkingDirectoryHandler(QFileSystemWatcher):
    """Handler to store and change the current working directory.

    Signals:
        cwd_changed: Emitted when the current working directory has changed.
            arg1: The new working directory.

    Attributes:
        _dir: The current working directory.
    """

    cwd_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._dir = None

        settings.signals.changed.connect(self._on_settings_changed)

    def chdir(self, directory):
        """Change the current working directory to directory."""
        directory = os.path.abspath(directory)
        if directory != self._dir:
            self._unmonitor(self._dir)
            self._dir = directory
            os.chdir(directory)
            self._monitor(directory)
            self.cwd_changed.emit(directory)

    def _monitor(self, directory):
        """Monitor the directory by adding it to QFileSystemWatcher."""
        if not settings.get_value(settings.Names.MONITOR_FS):
            return
        if not self.addPath(directory):
            logging.error("Cannot monitor %s", directory)
        else:
            logging.debug("Monitoring %s", directory)

    def _unmonitor(self, directory):
        """Unmonitor the directory by removing it from QFileSystemWatcher."""
        if directory is not None:
            self.removePath(directory)

    @pyqtSlot(str, object)
    def _on_settings_changed(self, setting, new_value):
        """Start/stop monitoring when the setting changed."""
        if setting == settings.Names.MONITOR_FS:
            if new_value:
                self._monitor(self._dir)
            else:
                logging.debug("Turning monitoring off")
                self._stop_monitoring()


handler = None


def init():
    """Initialize handler.

    This is required as working_directory is imported by the application but
    the QFileSystemWatcher only works appropriately once an application has
    been created.
    """
    global handler
    handler = WorkingDirectoryHandler() if handler is None else handler
