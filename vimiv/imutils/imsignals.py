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
        open_new_image: Emitted when a new image should be opened.
            arg1: Path to the new image.
        open_new_images: Emitted when a list of new images should be opened.
            arg1: List of new paths to the images.
            arg2: The path to be focused.
        new_image_opened: Emitted when the imstorage loaded a new path.
            arg1: Path of the new image.
        new_images_opened: Emitted when the imstorage loaded new paths.
            arg1: List of new paths.
        pixmap_loaded: Emitted when the imloader loaded a new pixmap.
            arg1: The QPixmap loaded.
        pixmap_updated: Emitted when the the pixmap was edited.
            arg1: The edited QPixmap.
        movie_loaded: Emitted when the imloader loaded a new animation.
            arg1: The QMovie loaded.
        svg_loaded: Emitted when the imloader loaded a new vector graphic.
            arg1: The path as the VectorGraphic class is constructed directly.
    """

    # Emited when new image path(s) should be opened
    open_new_image = pyqtSignal(str)
    open_new_images = pyqtSignal(list, str)

    # Emited when new image path(s) were opened
    new_image_opened = pyqtSignal(str)
    new_images_opened = pyqtSignal(list)

    # Tell the image to get a new object to display
    pixmap_loaded = pyqtSignal(QPixmap)
    movie_loaded = pyqtSignal(QMovie)
    svg_loaded = pyqtSignal(str)
    pixmap_updated = pyqtSignal(QPixmap)


imsignals = ImageSignalHandler()
