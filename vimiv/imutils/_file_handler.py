# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to deal with the actual image file."""

import enum
import os
import shutil
import tempfile
from typing import List

from PyQt5.QtCore import QObject, QCoreApplication
from PyQt5.QtGui import QPixmap, QImageReader, QMovie

from vimiv import api, utils, imutils
from vimiv.imutils import imtransform, immanipulate
from vimiv.utils import files, log, asyncrun

# We need the check as svg support is optional
try:
    from PyQt5.QtSvg import QSvgWidget
except ImportError:
    QSvgWidget = None


_logger = log.module_logger(__name__)


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


class ImageType(enum.IntEnum):
    """Enum class for different image widget types."""

    Pixmap = 0
    Svg = 1
    Movie = 2


class ImageFileHandler(QObject):
    """Handler to load and write images.

    The handler connects to the new_image_opened signal to retrieve the path of
    the current image. This path is opened with QImageReader and depending on
    the type of image one of the loaded signals is emitted with the generated
    QWidget. In addition to the loading the file handler provides a write
    command and is able to automatically write changes from transform or
    manipulate to file if wanted.

    Attributes:
        transform: Transform class to get rotate and flip from.
        manipulate: Manipulate class for e.g. brightness.

        _path: Path to the currently loaded QObject.
        _pixmaps: Pixmaps object storing different version of the loaded image.
    """

    @api.objreg.register
    def __init__(self):
        super().__init__()
        self._pixmaps = Pixmaps()

        self.transform = imtransform.Transform(self)
        self.manipulate = None

        self._path = ""
        self._image_type = None

        api.signals.new_image_opened.connect(self._on_new_image_opened)
        api.signals.all_images_cleared.connect(self._on_images_cleared)
        api.signals.image_changed.connect(self.reload)
        api.modes.MANIPULATE.first_entered.connect(self._init_manipulate)
        QCoreApplication.instance().aboutToQuit.connect(self._on_quit)

    @property
    def editable(self):
        """True if the currently opened image is transformable/manipulatable."""
        return self._image_type == ImageType.Pixmap

    @property
    def current(self):
        """The currently displayed pixmap.

        Upon setting a signal to update the image shown is emitted.
        """
        return self._pixmaps.current

    @current.setter
    def current(self, pixmap):
        self._pixmaps.current = pixmap
        reload_only = True
        api.signals.pixmap_loaded.emit(pixmap, reload_only)

    @property
    def original(self):
        """Original pixmap without any transformation or manipulations.

        Upon setting all edited pixmaps are reset as well.
        """
        return self._pixmaps.original

    @original.setter
    def original(self, pixmap) -> None:
        self._pixmaps.original = (
            self._pixmaps.transformed
        ) = self._pixmaps.current = pixmap

    @property
    def transformed(self):
        """Transformed pixmap without any manipulations applied.

        Upon setting the current pixmap gets updated and shown.
        """
        return self._pixmaps.transformed

    @transformed.setter
    def transformed(self, pixmap):
        self._pixmaps.transformed = pixmap
        self.current = pixmap

    @utils.slot
    def _on_new_image_opened(self, path: str):
        """Load proper displayable QWidget for a new image path."""
        self._maybe_write(self._path)
        self._load(path, reload_only=False)

    @utils.slot
    def _on_images_cleared(self):
        """Reset to default when all images were cleared."""
        self._path = ""
        self.original = None

    @utils.slot
    @api.commands.register(mode=api.modes.IMAGE)
    def reload(self):
        """Reload the current image."""
        self._load(self._path, reload_only=True)

    def _maybe_write(self, path, parallel=True):
        """Write image to disk if requested and it has changed.

        Args:
            path: Path to the image file.
        """
        if not api.settings.image.autowrite:
            self._reset()
        elif self.transform.changed or (
            self.manipulate is not None and self.manipulate.changed
        ):
            self.write_pixmap(self.current, path, original_path=path, parallel=parallel)

    @utils.slot
    def _on_quit(self):
        """Possibly write changes to disk on quit."""
        self._maybe_write(self._path, parallel=False)

    @utils.slot
    def _init_manipulate(self):
        self.manipulate = immanipulate.Manipulator(self)

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
        reader = QImageReader(path, file_format.encode("utf-8"))
        reader.setAutoTransform(True)  # Automatically apply exif orientation
        if not reader.canRead():
            log.error("Cannot read image %s", path)
            return
        # SVG
        if file_format == "svg" and QSvgWidget:
            # Do not store image and only emit with the path as the
            # VectorGraphic widget needs the path in the constructor
            self.original = None
            api.signals.svg_loaded.emit(path, reload_only)
            self._image_type = ImageType.Svg
        # Gif
        elif reader.supportsAnimation():
            movie = QMovie(path)
            if not movie.isValid() or movie.frameCount() == 0:
                log.error("Error reading animation %s: invalid data", path)
                return
            self.original = movie
            api.signals.movie_loaded.emit(self.current, reload_only)
            self._image_type = ImageType.Movie
        # Regular image
        else:
            pixmap = QPixmap.fromImageReader(reader)
            if reader.error():
                log.error("Error reading image %s: %s", path, reader.errorString())
                return
            self.original = pixmap
            api.signals.pixmap_loaded.emit(self.current, reload_only)
            self._image_type = ImageType.Pixmap
        self._path = path

    def _reset(self):
        """Reset transform and manipulate back to default."""
        self.transform.reset()
        if self.manipulate is not None:
            self.manipulate.reset()

    @api.commands.register(mode=api.modes.IMAGE)
    def write(self, path: List[str]):
        """Save the current image to disk.

        **syntax:** ``:write [path]``.

        positional arguments:
            * ``path``: Save to this path instead of the current one.
        """
        assert isinstance(path, list), "Must be list from nargs"
        self.write_pixmap(
            pixmap=self.current, path=" ".join(path), original_path=self._path
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
        self._reset()


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
