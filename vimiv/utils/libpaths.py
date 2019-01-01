# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to load paths for the library."""

import os

from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from vimiv.config import settings
from vimiv.utils import files, misc, working_directory


class LibraryPathHandler(QObject):
    """Handler to load paths for the library.

    The handler loads new paths when the working directory has changed and then
    emits a signal for the library which contains the data of the new paths.

    Signals:
        loaded: Emitted when a new list of paths for the library was loaded.
            arg1: The new list of paths.
    """

    loaded = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        working_directory.handler.cwd_changed.connect(self._on_cwd_changed)

    @pyqtSlot(str)
    def _on_cwd_changed(self, directory):
        """Load paths in new directory when the working directory changed."""
        self.load(directory)

    def load(self, directory):
        """Load paths in one directory for the library.

        Gets all supported files in the directory and emits the loaded signal.

        Args:
            directory: The directory to load.
        """
        show_hidden = settings.get_value(settings.Names.LIBRARY_SHOW_HIDDEN)
        paths = files.ls(directory, show_hidden=show_hidden)
        images, directories = files.get_supported(paths)
        data = []
        _extend_data(data, directories, dirs=True)
        _extend_data(data, images)
        self.loaded.emit(data)


handler = LibraryPathHandler()


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
        size = files.get_size(path)
        data.append((name, size))
