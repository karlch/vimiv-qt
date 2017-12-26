# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import logging

from PyQt5.QtCore import QRunnable, QObject, QThreadPool
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv.imutils.imcommunicate import signals
from vimiv.utils import objreg


class ImageLoader(QObject):

    _pool = QThreadPool.globalInstance()

    @objreg.register("imageloader")
    def __init__(self):
        super().__init__()
        signals.path_loaded.connect(self._on_path_loaded)

    def _on_path_loaded(self, path):
        loader = PathLoader(path)
        loader.run()


class PathLoader(QRunnable):
    """Load one image into the proper Qt class.

    Attributes:
        _path: Path to the image to load.
    """

    def __init__(self, path):
        super().__init__()
        self._path = path

    def run(self):
        reader = QImageReader(self._path)
        if not reader.canRead():
            logging.error("Cannot read image %s", self._path)
        elif reader.supportsAnimation():
            movie = QMovie(self._path)
            signals.movie_loaded.emit(movie)
        else:
            pixmap = QPixmap(self._path)
            signals.pixmap_loaded.emit(pixmap)
