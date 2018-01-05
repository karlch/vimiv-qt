# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Loader class to load image from path."""

import logging

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv.imutils import imsignals
from vimiv.utils import objreg

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


class ImageLoader(QObject):
    """Load proper displayable QObject for a path.

    Connects to the path_loaded signal to receive the name of the path. Emits
    either movie_loaded or image_loaded when the QWidget was created.
    """

    @objreg.register("imageloader")
    def __init__(self):
        super().__init__()
        self.image = None
        imsignals.connect(self._on_path_loaded, "path_loaded")

    @pyqtSlot(str)
    def _on_path_loaded(self, path):
        """Load proper displayable QWidget for a path."""
        reader = QImageReader(path)
        if not reader.canRead():
            logging.error("Cannot read image %s", path)
        elif reader.format().data().decode() == "svg" and QSvgWidget:
            # Do not store image and only emit with the path as the
            # VectorGraphic widget needs the path in the constructor
            self.image = None
            imsignals.emit("svg_loaded", path)
        elif reader.supportsAnimation():
            self.image = QMovie(path)
            imsignals.emit("movie_loaded", self.image)
        else:
            self.image = QPixmap(path)
            imsignals.emit("pixmap_loaded", self.image)


def current():
    """Convenience function to get currently displayed QObject."""
    loader = objreg.get("imageloader")
    return loader.image
