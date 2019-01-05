# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to load paths for the library."""

import os

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from vimiv.utils import files, misc, working_directory


class LibraryPathHandler(QObject):
    """Handler to load paths for the library.

    The handler loads new paths when the working directory has changed and then
    emits a signal for the library which contains the data of the new paths.

    Signals:
        loaded: Emitted when a new list of paths for the library was loaded.
            arg1: The new list of paths.
        changed: Emitted when the library paths content has changed.
            arg1: The new list of paths.
    """

    loaded = pyqtSignal(list)
    changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        working_directory.handler.changed.connect(self._on_dir_changed)
        working_directory.handler.loaded.connect(self._on_dir_loaded)

    @pyqtSlot(list, list)
    def _on_dir_loaded(self, images, directories):
        """Create data for the library when the directory has changed.

        Args:
            images: Images in the current directory.
            directories: Directories in the current directory.
        """
        self.loaded.emit(self._get_data(images, directories))

    @pyqtSlot(list, list)
    def _on_dir_changed(self, images, directories):
        """Create data for the library when the directory has changed.

        Args:
            images: Images in the current directory.
            directories: Directories in the current directory.
        """
        self.changed.emit(self._get_data(images, directories))

    @staticmethod
    def _get_data(images, directories):
        """Create data for images and directories."""
        data = []
        _extend_data(data, directories, dirs=True)
        _extend_data(data, images)
        return data


handler = None


def init():
    global handler
    handler = LibraryPathHandler() if handler is None else handler


def _extend_data(data, paths, dirs=False):
    """Extend list with list of data tuples for paths.

    Generates a tuple in the form of (name, size) for each path and adds it to
    the data list.

    Args:
        data: List to extend.
        paths: List of paths to generate data for.
        dirs: Whether all paths are directories.
    """
    for path in paths:
        name = os.path.basename(path)
        if dirs:
            name = misc.add_html("b", name + "/")
        try:
            size = files.get_size(path)
            data.append((name, size))
        except FileNotFoundError:  # Has been deleted in the meantime
            pass
