# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Loader class to load image from path."""

import logging

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv.imutils.imcommunicate import signals
from vimiv.utils import objreg


class ImageLoader(QObject):
    """Load proper displayable QWidget for a path.

    Connects to the path_loaded signal to receive the name of the path. Emits
    either movie_loaded or image_loaded when the QWidget was created.
    """

    @objreg.register("imageloader")
    def __init__(self):
        super().__init__()
        signals.path_loaded.connect(self._on_path_loaded)

    def _on_path_loaded(self, path):
        """Load proper displayable QWidget for a path."""
        reader = QImageReader(path)
        if not reader.canRead():
            logging.error("Cannot read image %s", path)
        elif reader.supportsAnimation():
            movie = QMovie(path)
            signals.movie_loaded.emit(movie)
        else:
            pixmap = QPixmap(path)
            signals.pixmap_loaded.emit(pixmap)
