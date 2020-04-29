# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to deal with the actual image file."""

import os
import shutil
import tempfile
from typing import List

from PyQt5.QtCore import QObject, QCoreApplication
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv import api, utils, imutils
from vimiv.utils import files, log, asyncrun, lazy

QtSvg = lazy.import_module("PyQt5.QtSvg", optional=True)


_logger = log.module_logger(__name__)


class ImageFileHandler(QObject):
    """Handler to load and write images.

    The handler connects to the new_image_opened signal to retrieve the path of
    the current image. This path is opened with QImageReader and depending on
    the type of image one of the loaded signals is emitted with the generated
    QWidget. In addition to the loading the file handler provides a write
    command and is able to automatically write changes from transform or
    manipulate to file if wanted.

    Attributes:
        _edit_handler: Handler to interact with any changes to the current image.
        _path: Path to the currently loaded QObject.
    """

    @api.objreg.register
    def __init__(self):
        super().__init__()
        self._path = ""
        self._edit_handler = imutils.EditHandler()

        api.signals.new_image_opened.connect(self._on_new_image_opened)
        api.signals.all_images_cleared.connect(self._on_images_cleared)
        api.signals.image_changed.connect(self.reload)
        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)

    @utils.slot
    def _on_new_image_opened(self, path: str):
        """Load proper displayable QWidget for a new image path."""
        self._maybe_write(self._path)
        self._load(path, reload_only=False)

    @utils.slot
    def _on_images_cleared(self):
        """Reset to default when all images were cleared."""
        self._path = ""
        self._edit_handler.clear()

    @utils.slot
    @api.commands.register(mode=api.modes.IMAGE)
    def reload(self):
        """Reload the current image."""
        self._load(self._path, reload_only=True)

    def _maybe_write(self, path, parallel=True):
        """Write image to disk if requested and it has changed.

        Args:
            path: Path to the image file.
            parallel: Write the image in an additional thread.
        """
        if not self._edit_handler.changed:
            return
        if api.settings.image.autowrite:
            self.write_pixmap(
                self._edit_handler.pixmap, path, original_path=path, parallel=parallel
            )
        else:
            self._edit_handler.reset()

    @utils.slot
    def _on_quit(self):
        """Possibly write changes to disk on quit."""
        self._maybe_write(self._path, parallel=False)

    def _load(self, path: str, reload_only: bool):
        """Load proper displayable QWidget for a path.

        This reads the image using QImageReader and then emits the appropriate
        *_loaded signal to tell the image to display a new object.
        """
        # Pass file format explicitly as imghdr does a much better job at this than the
        # file name based approach of QImageReader
        file_format = files.imghdr.what(path)
        if file_format is None:
            log.error("%s is not a valid image", path)
            return
        reader = QImageReader(path, file_format.encode())
        reader.setAutoTransform(True)  # Automatically apply exif orientation
        if not reader.canRead():
            log.error("Cannot read image %s", path)
            return
        # SVG
        if file_format == "svg" and QtSvg is not None:
            # Do not store image and only emit with the path as the
            # VectorGraphic widget needs the path in the constructor
            api.signals.svg_loaded.emit(path, reload_only)
            self._edit_handler.clear()
        # Gif
        elif reader.supportsAnimation():
            movie = QMovie(path)
            if not movie.isValid() or movie.frameCount() == 0:
                log.error("Error reading animation %s: invalid data", path)
                return
            api.signals.movie_loaded.emit(movie, reload_only)
            self._edit_handler.clear()
        # Regular image
        else:
            pixmap = QPixmap.fromImageReader(reader)
            if reader.error():
                log.error("Error reading image %s: %s", path, reader.errorString())
                return
            self._edit_handler.pixmap = pixmap
            api.signals.pixmap_loaded.emit(pixmap, reload_only)
        self._path = path

    @api.commands.register(mode=api.modes.IMAGE)
    def write(self, path: List[str]):
        """Save the current image to disk.

        **syntax:** ``:write [path]``.

        positional arguments:
            * ``path``: Save to this path instead of the current one.
        """
        assert isinstance(path, list), "Must be list from nargs"
        self.write_pixmap(
            pixmap=self._edit_handler.pixmap,
            path=" ".join(path),
            original_path=self._path,
        )

    def write_pixmap(self, pixmap, path=None, original_path=None, parallel=True):
        """Write a pixmap to disk.

        Args:
            pixmap: The QPixmap to write.
            path: The path to save the pixmap to.
            original_path: Original path of the opened pixmap.
            parallel: Perform operation in parallel.
        """
        if not path:
            path = original_path = self._path
        if parallel:
            asyncrun(write_pixmap, pixmap, path, original_path)
        else:
            write_pixmap(pixmap, path, original_path)
        self._edit_handler.reset()


def write_pixmap(pixmap, path, original_path):
    """Write pixmap to file.

    This requires both the path to write to and the original path as Exif data
    may be copied from the original path to the new copy. The procedure is to
    write the path to a temporary file first, transplant the Exif data to the
    temporary file if possible and finally rename the temporary file to the
    final path. The renaming is done as it is an atomic operation and we may be
    overriding the existing file.

    Args:
        pixmap: The QPixmap to write.
        path: Path to write the pixmap to.
        original_path: Original path of the opened pixmap to retrieve exif information.
    """
    try:
        _can_write(pixmap, path)
        _logger.debug("Image is writable")
        _write(pixmap, path, original_path)
        log.info("Saved %s", path)
    except WriteError as e:
        log.error(str(e))


def _can_write(pixmap, path):
    """Check if it is possible to save the current path.

    See write_pixmap for the args description.

    Raises:
        WriteError if writing is not possible.
    """
    if not isinstance(pixmap, QPixmap):
        raise WriteError("Cannot write animations")
    if os.path.exists(path):  # Override current path
        reader = QImageReader(path)
        if not reader.canRead():
            raise WriteError(f"Path '{path}' exists and is not an image")


def _write(pixmap, path, original_path):
    """Write pixmap to disk.

    See write_pixmap for the args description.
    """
    # Get pixmap type
    _, ext = os.path.splitext(path)
    # First create temporary file and then move it to avoid race conditions
    handle, filename = tempfile.mkstemp(suffix=ext)
    os.close(handle)
    pixmap.save(filename)
    # Copy exif info from original file to new file
    imutils.exif.copy_exif(original_path, filename)
    shutil.move(filename, path)
    # Check if valid image was created
    if not os.path.isfile(path):
        raise WriteError("File not written, unknown exception")
    if not files.is_image(path):
        os.remove(path)
        raise WriteError("No valid image written. Is the extention valid?")


class WriteError(Exception):
    """Raised when write_pixmap encounters problems."""
