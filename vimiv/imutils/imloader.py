# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Loader class to load image from path."""

import logging

from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv.imutils.imsignals import imsignals
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

    @objreg.register
    def __init__(self):
        super().__init__()
        self.image = None
        imsignals.path_loaded.connect(self._on_path_loaded)

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
            imsignals.svg_loaded.emit(path)
        elif reader.supportsAnimation():
            self.image = QMovie(path)
            imsignals.movie_loaded.emit(self.image)
        else:
            self.image = QPixmap(path)
            imsignals.pixmap_loaded.emit(self.image)


def instance():
    return objreg.get(ImageLoader)


def current():
    """Convenience function to get currently displayed QObject."""
    return instance().image


def set_pixmap(pixmap):
    instance().image = pixmap
