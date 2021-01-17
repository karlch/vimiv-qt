# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Image reader classes to read images from file to Qt objects."""

import abc
from typing import Dict, Callable

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImageReader, QPixmap, QImage

from .files import imghdr

external_handler: Dict[str, Callable[[str], QPixmap]] = {}


class BaseReader(abc.ABC):
    """Base class for image readers.

    Provides the basic interface. Child classes must implement the get_pixmap method
    which reads the file from disk and returns a QPixmap. In addition, the classmethod
    supports must be implemented to define the supported image formats. For
    optimization, the get_image method can also be provided. This method is called when
    retrieving thumbnails.
    """

    def __init__(self, path: str, file_format: str):
        self.path = path
        self.file_format = file_format

    @property
    def is_vectorgraphic(self) -> bool:
        return self.file_format == "svg"

    @property
    def is_animation(self) -> bool:
        return False

    @abc.abstractmethod
    def get_pixmap(self) -> QPixmap:
        """Read self.path from disk and return a QPixmap."""

    def get_image(self, size: int) -> QImage:
        """Read self.path from disk and return a scaled QImage."""
        pixmap = self.get_pixmap().scaled(size, size, Qt.KeepAspectRatio)
        return pixmap.toImage()

    @classmethod
    @abc.abstractclassmethod
    def supports(cls, file_format: str) -> bool:
        """Return True if the file_format is supported."""


class QtReader(BaseReader):
    """Image reader using Qt's QImageReader implementation under the hood."""

    def __init__(self, path: str, file_format: str):
        super().__init__(path, file_format)
        self._handler = QImageReader(path, file_format.encode())
        self._handler.setAutoTransform(True)
        if not self._handler.canRead():
            # TODO
            raise ValueError(f"'{path}' cannot be read as image")

    @classmethod
    def supports(cls, file_format: str) -> bool:
        return file_format in QImageReader.supportedImageFormats()

    @property
    def is_animation(self) -> bool:
        return self._handler.supportsAnimation()

    def get_pixmap(self) -> QPixmap:
        """Retrieve the pixmap directly from the image reader."""
        pixmap = QPixmap.fromImageReader(self._handler)
        if self._handler.error():
            raise ValueError(
                f"Error reading image '{self.path}': {self._handler.errorString()}"
            )
        return pixmap

    def get_image(self, size: int) -> QImage:
        """Retrieve the down-scaled image directly from the image reader."""
        qsize = self._handler.size()
        qsize.scale(size, size, Qt.KeepAspectRatio)
        self._handler.setScaledSize(qsize)
        return self._handler.read()


class ExternalReader(BaseReader):
    """Image reader using any external handlers from the api."""

    @classmethod
    def supports(cls, file_format: str) -> bool:
        return file_format in external_handler

    def get_pixmap(self) -> QPixmap:
        handler = external_handler[self.file_format]
        return handler(self.path)


READERS = [QtReader, ExternalReader]


def get_reader(path: str) -> BaseReader:
    """Retrieve the appropriate image reader class for path."""
    error = ValueError(f"'{path}' cannot be read as image")
    try:
        file_format = imghdr.what(path)
    except OSError:
        raise error
    if file_format is None:
        raise error

    for readercls in READERS:
        if readercls.supports(file_format):
            return readercls(path, file_format)

    raise error
