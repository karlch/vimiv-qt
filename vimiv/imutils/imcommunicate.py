# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Class to handle communication between image and utilities."""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie


class ImageCommunicate(QObject):
    """Class with signals to communicate between image and utilities.

    Signals:
        image_loaded: Emitted with the path when a new image was loaded.
        pixmap_loaded: Emitted with the QPixmap when a new image was loaded.
        movie_loaded: Emitted with the QMovie when a new image was loaded.
        paths_loaded: Emitted with the list of paths when new paths were
            loaded.
        update_index: Emitted with the index when the image should select a new
            index.
        update_path: Emitted with the path when the image should select a new
            path.
        load_paths: Emitted with the list of paths when new paths should be
            loaded.
    """

    # Tell the storage to set new things
    update_index = pyqtSignal(int)
    update_path = pyqtSignal(str)
    update_paths = pyqtSignal(list, int)

    # Tell the loaders to load new images
    path_loaded = pyqtSignal(str)
    paths_loaded = pyqtSignal(list)

    # Tell the image to get a new object to display
    pixmap_loaded = pyqtSignal(QPixmap)
    movie_loaded = pyqtSignal(QMovie)

    # Tell the library that it may make sense to update
    maybe_update_library = pyqtSignal(str)
    # Tell transformation to write to file
    maybe_write_file = pyqtSignal(str)


signals = ImageCommunicate()
