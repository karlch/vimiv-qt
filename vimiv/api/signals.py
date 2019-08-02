# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Namespace for signals exposed via the api."""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie


class _SignalHandler(QObject):
    """Qt signal handler class for signals exposed via the api.

    Signals:
        load_images: Emitted when new images should be loaded by the filelist.
            arg1: List of new image paths.

        new_image_opened: Emitted when the filelist loaded a new path.
            arg1: Path of the new image.
        new_images_opened: Emitted when the filelist loaded new paths.
            arg1: List of new paths.
        all_images_cleared: Emitted when there are no more paths in the filelist.

        image_changed: Emitted when the current image changed on disk.

        pixmap_loaded: Emitted when the file handler loaded a new pixmap.
            arg1: The QPixmap loaded.
            arg2: True if it is only reloaded.
        movie_loaded: Emitted when the file handler loaded a new animation.
            arg1: The QMovie loaded.
            arg2: True if it is only reloaded.
        svg_loaded: Emitted when the file handler loaded a new vector graphic.
            arg1: The path as the VectorGraphic class is constructed directly.
            arg2: True if it is only reloaded.
    """

    # Emitted when new images should be loaded
    load_images = pyqtSignal(list)

    # Emited when new image path(s) were opened
    new_image_opened = pyqtSignal(str)
    new_images_opened = pyqtSignal(list)
    all_images_cleared = pyqtSignal()

    # Emitted when the current image changed on disk
    image_changed = pyqtSignal()

    # Tell the image to get a new object to display
    pixmap_loaded = pyqtSignal(QPixmap, bool)
    movie_loaded = pyqtSignal(QMovie, bool)
    svg_loaded = pyqtSignal(str, bool)


_signal_handler = _SignalHandler()  # Instance of Qt signal handler to work with

# Convenience access to the signals
load_images = _signal_handler.load_images
new_image_opened = _signal_handler.new_image_opened
new_images_opened = _signal_handler.new_images_opened
all_images_cleared = _signal_handler.all_images_cleared
image_changed = _signal_handler.image_changed
pixmap_loaded = _signal_handler.pixmap_loaded
movie_loaded = _signal_handler.movie_loaded
svg_loaded = _signal_handler.svg_loaded
