# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Single class storing signals for image utilities.

Module Attributes:
    imsignals: The created ImageSignalHandler class to store the signals.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie


class ImageSignalHandler(QObject):
    """Store signals for image utilities as class attributes.

    Signals:
        update_index: Emitted when a new index should be opened.
            arg1: Integer of the new index to select.
        update_path: Emitted when a new image path should be opened.
            arg1: Path of the new image.
        update_paths: Emitted when new paths should be opened.
            arg1: List of new paths.
        path_loaded: Emitted when the imstorage loaded a new path.
            arg1: Path of the new image.
        paths_loaded: Emitted when the imstorage loaded new paths.
            arg1: List of new paths.
        pixmap_loaded: Emitted when the imloader loaded a new pixmap.
            arg1: The QPixmap loaded.
        pixmap_updated: Emitted when the the pixmap was edited.
            arg1: The edited QPixmap.
        movie_loaded: Emitted when the imloader loaded a new animation.
            arg1: The QMovie loaded.
        svg_loaded: Emitted when the imloader loaded a new vector graphic.
            arg1: The path as the VectorGraphic class is constructed directly.
        maybe_update_library: Emitted when the working directory may have
                changed.
            arg1: The new working directory.
        maybe_write_file: Emitted when the selected image changes and the
                imwriter might have write changes to disk.
            arg1: The path to the file that might have to be written to disk.

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
    svg_loaded = pyqtSignal(str)
    pixmap_updated = pyqtSignal(QPixmap)

    # Tell the library that it may make sense to update
    maybe_update_library = pyqtSignal(str)
    # Tell transformation to write to file
    maybe_write_file = pyqtSignal(str)


imsignals = ImageSignalHandler()
