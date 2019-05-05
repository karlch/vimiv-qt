# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various utilities to work with in image mode."""

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QPixmap, QMovie

from .filelist import load, current, pathlist
from .filelist import SignalHandler as _FilelistSignalHandler
from ._file_handler import ImageFileHandler as _ImageFileHandler


def init():
    """Initialize the classes needed for imutils."""
    _FilelistSignalHandler()
    _ImageFileHandler()


class _ImageSignalHandler(QObject):
    """Store signals for image utilities as class attributes.

    Signals:
        new_image_opened: Emitted when the imstorage loaded a new path.
            arg1: Path of the new image.
        new_images_opened: Emitted when the imstorage loaded new paths.
            arg1: List of new paths.
        all_images_cleared: Emitted when there are no more paths in imstorage.
        pixmap_loaded: Emitted when the imloader loaded a new pixmap.
            arg1: The QPixmap loaded.
        pixmap_updated: Emitted when the the pixmap was edited.
            arg1: The edited QPixmap.
        movie_loaded: Emitted when the imloader loaded a new animation.
            arg1: The QMovie loaded.
        svg_loaded: Emitted when the imloader loaded a new vector graphic.
            arg1: The path as the VectorGraphic class is constructed directly.
    """

    # Emited when new image path(s) were opened
    new_image_opened = pyqtSignal(str)
    new_images_opened = pyqtSignal(list)
    all_images_cleared = pyqtSignal()

    # Tell the image to get a new object to display
    pixmap_loaded = pyqtSignal(QPixmap)
    movie_loaded = pyqtSignal(QMovie)
    svg_loaded = pyqtSignal(str)
    pixmap_updated = pyqtSignal(QPixmap)


_signal_handler = _ImageSignalHandler()  # Instance of Qt signal handler to work with


# Convenience access to the signals
new_image_opened = _signal_handler.new_image_opened
new_images_opened = _signal_handler.new_images_opened
all_images_cleared = _signal_handler.all_images_cleared
pixmap_loaded = _signal_handler.pixmap_loaded
movie_loaded = _signal_handler.movie_loaded
svg_loaded = _signal_handler.svg_loaded
pixmap_updated = _signal_handler.pixmap_updated
