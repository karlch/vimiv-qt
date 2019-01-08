# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to deal with the actual image file."""

import logging
import os
import tempfile

from PyQt5.QtCore import (QObject, QRunnable, QThreadPool, QCoreApplication,
                          pyqtSlot)
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv.commands import commands
from vimiv.config import settings
from vimiv.imutils import imtransform, imsignals, immanipulate
from vimiv.modes import Modes
from vimiv.utils import objreg, files

# We need the check as exif support is optional
try:
    import piexif
except ImportError:
    piexif = None

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


class Pixmaps:
    """Simple storage class for different pixmap versions.

    Class Attributes:
        current: The current possibly transformed and manipulated pixmap.
        original: The original unedited pixmap.
        transformed: The possibly transformed but unmanipulated pixmap.
    """

    current = None
    original = None
    transformed = None


class ImageFileHandler(QObject):
    """Handler to load and write images.

    TODO

    Attributes:
        transform: Transform class to get rotate and flip from.
        manipulate: Manipulate class for e.g. brightness.

        _path: Path to the currently loaded QObject.
        _pixmaps: Pixmaps object storing different version of the loaded image.
    """

    _pool = QThreadPool.globalInstance()

    @objreg.register
    def __init__(self):
        super().__init__()
        self._pixmaps = Pixmaps()

        self.transform = imtransform.Transform(self)
        self.manipulate = immanipulate.Manipulator(self)

        self._path = ""

        imsignals.imsignals.new_image_opened.connect(self._on_new_image_opened)
        imsignals.imsignals.all_images_cleared.connect(self._on_images_cleared)
        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)

    @property
    def current(self):
        """Current pixmap as property to disallow setting."""
        return self._pixmaps.current

    @property
    def original(self):
        """Original pixmap as property to disallow setting."""
        return self._pixmaps.original

    @property
    def transformed(self):
        """Transformed pixmap as property to disallow setting."""
        return self._pixmaps.transformed

    @pyqtSlot(str)
    def _on_new_image_opened(self, path):
        """Load proper displayable QWidget for a new image path."""
        self._maybe_write(self._path)
        self._load(path)

    @pyqtSlot()
    def _on_images_cleared(self):
        """Reset to default when all images were cleared."""
        self._path = ""
        self._set_original(None)

    def _maybe_write(self, path):
        """Write image to disk if requested and it has changed.

        Args:
            path: Path to the image file.
        """
        if not settings.get_value(settings.Names.IMAGE_AUTOWRITE):
            self._reset()
        elif self.transform.changed() or self.manipulate.changed():
            self.write_pixmap(self.current, path)

    @pyqtSlot()
    def _on_quit(self):
        """Possibly write changes to disk on quit."""
        self._maybe_write(self._path)
        self._pool.waitForDone()

    def _load(self, path):
        """Load proper displayable QWidget for a path.

        This reads the image using QImageReader and then emits the appropriate
        *_loaded signal to tell the image to display a new object.
        """
        reader = QImageReader(path)
        reader.setAutoTransform(True)  # Automatically apply exif orientation
        if not reader.canRead():
            logging.error("Cannot read image %s", path)
            return
        if reader.format().data().decode() == "svg" and QSvgWidget:
            # Do not store image and only emit with the path as the
            # VectorGraphic widget needs the path in the constructor
            self._set_original(None)
            imsignals.imsignals.svg_loaded.emit(path)
        elif reader.supportsAnimation():
            self._set_original(QMovie(path))
            imsignals.imsignals.movie_loaded.emit(self.current)
        else:
            self._set_original(QPixmap(path))
            imsignals.imsignals.pixmap_loaded.emit(self.current)
        self._path = path

    def _reset(self):
        self.transform.reset()
        self.manipulate.reset()

    @commands.argument("path", nargs="*")
    @commands.register(mode=Modes.IMAGE)
    def write(self, path):
        """Save the current image to disk.

        **syntax:** ``:write [path]``.

        positional arguments:
            * ``path``: Save to this path instead of the current one.
        """
        assert isinstance(path, list), "Must be list from nargs"
        path = " ".join(path) if path else self._path
        self.write_pixmap(self.current, path, self._path)

    def write_pixmap(self, pixmap, path, original_path):
        """Write a pixmap to disk.

        Args:
            pixmap: The QPixmap to write.
            path: The path to save the pixmap to.
            original_path: Original path of the opened pixmap.
        """
        runner = WriteImageRunner(pixmap, path, original_path)
        self._pool.start(runner)
        self._reset()

    def update_pixmap(self, pixmap):
        """Set the current pixmap and emit signal to update image shown."""
        self._pixmaps.current = pixmap
        imsignals.imsignals.pixmap_updated.emit(pixmap)

    def update_transformed(self, pixmap):
        """Set the transformed and current pixmap."""
        self._pixmaps.transformed = pixmap
        self.update_pixmap(pixmap)

    def _set_original(self, pixmap):
        """Set the original pixmap."""
        self._pixmaps.original = self._pixmaps.transformed \
            = self._pixmaps.current = pixmap


class WriteImageRunner(QRunnable):
    """Write QPixmap to file in an extra thread.

    This requires both the path to write to and the original path as Exif data
    may be copied from the original path to the new copy. The procedure is to
    write the path to a temporary file first, transplant the Exif data to the
    temporary file if possible and finally rename the temporary file to the
    final path. The renaming is done as it is an atomic operation and we may be
    overriding the existing file.

    Attributes:
        _pixmap: The QPixmap to write.
        _path: Path to write the pixmap to.
        _original_path: Original path of the opened pixmap.
    """

    def __init__(self, pixmap, path, original_path):
        super().__init__()
        self._pixmap = pixmap
        self._path = path
        self._original_path = original_path

    def run(self):
        """Write image to file."""
        logging.info("Saving %s...", self._path)
        try:
            self._can_write()
            logging.debug("Image is writable")
            self._write()
            logging.info("Saved %s", self._path)
        except WriteError as e:
            logging.error(str(e))

    def _can_write(self):
        """Check if the given path is writable.

        Raises WriteError if writing is not possible.

        Args:
            path: Path to write to.
            image: QPixmap to write.
        """
        if not isinstance(self._pixmap, QPixmap):
            raise WriteError("Cannot write animations")
        # Override current path
        elif os.path.exists(self._path):
            reader = QImageReader(self._path)
            if not reader.canRead():
                raise WriteError(
                    "Path '%s' exists and is not an image" % (self._path))

    def _write(self):
        """Write pixmap to disk."""
        # Get pixmap type
        _, ext = os.path.splitext(self._path)
        # First create temporary file and then move it to avoid race conditions
        handle, filename = tempfile.mkstemp(dir=os.getcwd(), suffix=ext)
        os.close(handle)
        self._pixmap.save(filename)
        # Copy exif info from original file to new file
        if piexif is not None:
            self._copy_exif(self._original_path, filename)
        os.rename(filename, self._path)
        # Check if valid image was created
        if not os.path.isfile(self._path):
            raise WriteError("File not written, unknown exception")
        elif not files.is_image(self._path):
            os.remove(self._path)
            raise WriteError("No valid image written. Is the extention valid?")

    @staticmethod
    def _copy_exif(src, dest):
        """Copy exif information from src to dest."""
        try:
            piexif.transplant(src, dest)
            logging.debug("Succesfully wrote exif data for '%s'", dest)
        except piexif.InvalidImageDataError:  # File is not a jpg
            logging.debug("File format for '%s' does not support exif", dest)
        except ValueError:
            logging.debug("No exif data in '%s'", dest)


class WriteError(Exception):
    """Raised when the WriteImageRunner encounters problems."""
