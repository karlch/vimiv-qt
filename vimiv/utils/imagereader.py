# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Image reader classes to read images from file to Qt objects."""

import abc
from typing import Dict, Callable

from vimiv.qt.core import Qt
from vimiv.qt.gui import QImageReader, QPixmap, QImage

from vimiv.utils import imageheader

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
        pixmap = self.get_pixmap().scaled(
            size, size, Qt.AspectRatioMode.KeepAspectRatio
        )
        return pixmap.toImage()

    @classmethod
    @abc.abstractmethod
    def supports(cls, file_format: str) -> bool:
        """Return True if the file_format is supported."""


class QtReader(BaseReader):
    """Image reader using Qt's QImageReader implementation under the hood."""

    def __init__(self, path: str, file_format: str):
        super().__init__(path, file_format)
        self._handler = QImageReader(path, file_format.encode())  # type: ignore[call-overload,unused-ignore]
        self._handler.setAutoTransform(True)
        if not self._handler.canRead():
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
        if pixmap.isNull():
            raise ValueError(
                f"Error reading image '{self.path}': {self._handler.errorString()}"
            )
        return pixmap

    def get_image(self, size: int) -> QImage:
        """Retrieve the down-scaled image directly from the image reader."""
        qsize = self._handler.size()
        qsize.scale(size, size, Qt.AspectRatioMode.KeepAspectRatio)
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


def get_reader(path: str) -> BaseReader:
    """Retrieve the appropriate image reader class for path."""
    error = ValueError(f"'{path}' cannot be read as image")
    try:
        file_format = imageheader.detect(path)
    except OSError:
        raise error
    if file_format is None:
        raise error

    # Prioritize external reader over qt reader to ensure that a external reader can
    # overwrite a default reader for the same image format.
    # Used when one wants to use a different methods for generating the QPixmap than how
    # Qt does it, for a given format.
    if ExternalReader.supports(file_format):
        return ExternalReader(path, file_format)

    if QtReader.supports(file_format):
        return QtReader(path, file_format)

    raise error
