# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to deal with the actual image file."""

import logging
import os
import tempfile

from PyQt5.QtCore import (QObject, QRunnable, QThreadPool, QCoreApplication,
                          pyqtSlot)
from PyQt5.QtGui import QPixmap, QImageReader

from vimiv.commands import commands
from vimiv.config import settings
from vimiv.imutils import (imtransform, imloader, imstorage, imsignals,
                           immanipulate)
from vimiv.utils import objreg, files

# We need the check as exif support is optional
try:
    import piexif
except ImportError:
    piexif = None


class ImageFileHandler(QObject):
    """Handler to check for changes and write images to disk.

    The handler connects to the maybe_write_file signal, checks if the user
    wants writing and if the image has changed and if so writes the file to
    disk applying all changes.

    Also provides a generic :write command to force writing an image to disk
    with possibly a new filename.

    Attributes:
        transform: Transform class to get rotate and flip from.
    """

    _pool = QThreadPool.globalInstance()

    @objreg.register("imfile_handler")
    def __init__(self):
        super().__init__()
        self.transform = imtransform.Transform()
        self.manipulate = immanipulate.Manipulator()
        imsignals.imsignals.maybe_write_file.connect(self._maybe_write)
        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)

    def pixmap(self):
        """Convenience method to get the fully edited pixmap."""
        pixmap = imloader.current()
        return self.transform.transform_pixmap(pixmap)

    @pyqtSlot(str)
    def _maybe_write(self, path):
        """Write image to disk if requested and it has changed.

        Args:
            path: Path to the image file.
        """
        if not settings.get_value(settings.Names.IMAGE_AUTOWRITE):
            self._reset()
        elif self.transform.changed() or self.manipulate.changed():
            self.write([path])

    @pyqtSlot()
    def _on_quit(self):
        """Possibly write changes to disk on quit."""
        path = imstorage.current()
        self._maybe_write(path)
        self._pool.waitForDone()

    def _reset(self):
        self.transform.reset()

    @commands.argument("path", nargs="*")
    @commands.register(mode="image", instance="imfile_handler")
    def write(self, path):
        """Save the current image to disk.

        **syntax:** ``:write [path]``.

        positional arguments:
            * ``path``: Save to this path instead of the current one.
        """
        assert isinstance(path, list), "Must be list from nargs"
        path = " ".join(path) if path else imstorage.current()
        pixmap = self.pixmap()
        self.write_pixmap(pixmap, path)

    def write_pixmap(self, pixmap, path):
        """Write a pixmap to disk.

        Args:
            pixmap: The QPixmap to write.
            path: The path to save the pixmap to.
        """
        runner = WriteImageRunner(pixmap, path)
        self._pool.start(runner)
        self._reset()


class WriteImageRunner(QRunnable):
    """Write QPixmap to file in an extra thread.

    Attributes:
        _pixmap: The QPixmap to write.
        _path: Path to write the pixmap to.
    """

    def __init__(self, pixmap, path):
        super().__init__()
        self._pixmap = pixmap
        self._path = path

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
        # Copy exif info from old file to new file
        if piexif is not None:
            self._copy_exif(self._path, filename)
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
        except piexif.InvalidImageDataError:  # File is not a jpg
            pass


class WriteError(Exception):
    """Raised when the WriteImageRunner encounters problems."""
