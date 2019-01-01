# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to take care of the current working directory."""

import os

from PyQt5.QtCore import QObject, pyqtSignal


class WorkingDirectoryHandler(QObject):
    """Handler to store and change the current working directory.

    Signals:
        cwd_changed: Emitted when the current working directory has changed.
            arg1: The new working directory.
    """

    cwd_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._dir = os.path.expanduser("~")

    def chdir(self, directory):
        """Change the current working directory to directory."""
        directory = os.path.abspath(directory)
        if directory != self._dir:
            self._dir = directory
            os.chdir(directory)
            self.cwd_changed.emit(directory)


handler = WorkingDirectoryHandler()
