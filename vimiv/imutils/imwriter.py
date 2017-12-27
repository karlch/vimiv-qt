# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions to write an image to disk."""

import logging
import os
import tempfile

from PyQt5.QtCore import QRunnable, QThreadPool, QObject
from PyQt5.QtGui import QPixmap, QImageReader

from vimiv.commands import commands
from vimiv.imutils import imstorage, imloader
from vimiv.utils import objreg


class ImageWriter(QObject):
    """Write images to disk using a thread pool."""

    _pool = QThreadPool.globalInstance()

    @objreg.register("imagewriter")
    def __init__(self):
        super().__init__()

    @commands.argument("path", nargs="*")
    @commands.register(mode="image", instance="imagewriter")
    def write(self, path):
        """Write the image to disk.

        Args:
            path: Use path instead of currently loaded path.
        """
        path = " ".join(path) if path else imstorage.current()  # List from nargs
        pixmap = imloader.current()
        self.write_pixmap(pixmap, path)

    def write_pixmap(self, pixmap, path):
        """Write a pixmap to disk.

        Args:
            pixmap: The QPixmap to write.
            path: The path to save the pixmap to.
        """
        runner = WriteImageRunner(pixmap, path)
        self._pool.start(runner)


class WriteImageRunner(QRunnable):
    """Write QPixmap to file in an extra thread."""

    def __init__(self, pixmap, path):
        super().__init__()
        self._pixmap = pixmap
        self._path = path

    def run(self):
        logging.info("Saving %s", self._path)
        try:
            self._can_write()
        except WriteError as e:
            logging.error(str(e))
            return
        self._write()
        if not os.path.isfile(self._path):
            logging.error("Writing failed, was the extension valid?")
        else:
            logging.info("Successfully saved %s", self._path)

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
        os.rename(filename, self._path)


class WriteError(Exception):
    """Raised when the WriteImageRunner encounters problems."""
