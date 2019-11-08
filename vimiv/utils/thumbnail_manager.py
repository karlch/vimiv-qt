# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""ThumbnailManager to create thumbnails asynchronously.

The ThumbnailManager class uses the Creator classes to create thumbnails for a
list of paths. When one thumbnail was created, the 'created' signal is emitted
with the index and the QPixmap of the generated thumbnail for the thumbnail
widget to update.
"""

import hashlib
import os
import tempfile
from contextlib import suppress
from typing import Dict, List

from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImageReader, QImage

import vimiv
from vimiv.utils import xdg, Pool


KEY_URI = "Thumb::URI"
KEY_MTIME = "Thumb::MTime"
KEY_SIZE = "Thumb::Size"
KEY_WIDTH = "Thumb::Image::Width"
KEY_HEIGHT = "Thumb::Image::Height"
KEY_SOFTWARE = "Software"


class ThumbnailManager(QObject):
    """Manager to create thumbnails for the thumbnail widgets asynchronously.

    Starts the ThumbnailsAsyncCreator class for a list of paths in an extra
    thread.

    Attributes:
        directory: Directory to store generated thumbnails in.
        fail_directory: Directory to store information on failed thumbnails in.
        fail_pixmap: QPixmap to display when thumbnail generation failed.

        _large: Create large thumbnails.

    Signals:
        created: Emitted with index and pixmap when a thumbnail was created.
    """

    created = pyqtSignal(int, QIcon)
    pool = Pool.get(globalinstance=False)

    def __init__(self, fail_pixmap: QPixmap, large: bool = True):
        super().__init__()
        self.large = large
        # Thumbnail creation should take no longer than 1 s
        self.pool.setExpiryTimeout(1000)

        directory = os.path.join(xdg.user_cache_dir(), "thumbnails")
        self.directory = (
            os.path.join(directory, "large")
            if large
            else os.path.join(directory, "normal")
        )
        self.fail_directory = os.path.join(
            directory, "fail", f"vimiv-{vimiv.__version__}"
        )
        xdg.makedirs(self.directory, self.fail_directory)
        self.fail_pixmap = fail_pixmap

    def create_thumbnails_async(self, paths: List[str]) -> None:
        """Start ThumbnailsCreator for each path to create thumbnails.

        Args:
            paths: Paths to create thumbnails for.
        """
        self.pool.clear()
        for i, path in enumerate(paths):
            self.pool.start(ThumbnailCreator(i, path, self))


class ThumbnailCreator(QRunnable):
    """Create thumbnail for one path.

    Implements freedesktop's thumbnail managing standard:
    https://specifications.freedesktop.org/thumbnail-spec/thumbnail-spec-latest.html

    Attributes:
        _index: Index of the thumbnail in the thumbnail widget.
        _path: Path to the original image.
        _manager: The ThumbnailManager object used for callback.
    """

    def __init__(self, index: int, path: str, manager: ThumbnailManager):
        super().__init__()
        self._index = index
        self._path = path
        self._manager = manager

    def run(self) -> None:
        """Create thumbnail and emit the managers created signal."""
        thumbnail_path = self._get_thumbnail_path(self._path)
        with suppress(FileNotFoundError):
            pixmap = (
                self._maybe_recreate_thumbnail(self._path, thumbnail_path)
                if os.path.exists(thumbnail_path)
                else self._create_thumbnail(self._path, thumbnail_path)
            )
            self._manager.created.emit(self._index, QIcon(pixmap))

    def _get_thumbnail_path(self, path: str) -> str:
        filename = self._get_thumbnail_filename(path)
        return os.path.join(self._manager.directory, filename)

    @staticmethod
    def _get_source_uri(path: str) -> str:
        return "file://" + os.path.abspath(os.path.expanduser(path))

    def _get_thumbnail_filename(self, path: str) -> str:
        uri = self._get_source_uri(path)
        return hashlib.md5(bytes(uri, "UTF-8")).hexdigest() + ".png"

    @staticmethod
    def _get_source_mtime(path: str) -> int:
        return int(os.path.getmtime(path))

    def _create_thumbnail(self, path: str, thumbnail_path: str) -> QPixmap:
        """Create thumbnail for an image.

        Args:
            path: Path to the image for which the thumbnail is created.
            thumbnail_path: Path to which the thumbnail is stored.
        Returns:
            The created QPixmap.
        """
        # Cannot access source
        if not os.access(path, os.R_OK):
            return self._manager.fail_pixmap
        size = 256 if self._manager.large else 128
        reader = QImageReader(path)
        reader.setAutoTransform(True)  # Automatically apply exif orientation
        if reader.canRead():
            qsize = reader.size()
            qsize.scale(size, size, Qt.KeepAspectRatio)
            reader.setScaledSize(qsize)
            image = reader.read()
            # Image was deleted in the time between reader.read() and now
            try:
                attributes = self._get_thumbnail_attributes(path, image)
            except FileNotFoundError:
                return self._manager.fail_pixmap
            for key, value in attributes.items():
                image.setText(key, value)
            # First create temporary file and then move it. This avoids
            # problems with concurrent access of the thumbnail cache, since
            # "move" is an atomic operation
            handle, tmp_filename = tempfile.mkstemp(dir=self._manager.directory)
            os.close(handle)
            os.chmod(tmp_filename, 0o600)
            image.save(tmp_filename, format="png")
            os.replace(tmp_filename, thumbnail_path)
            return QPixmap(image)
        return self._manager.fail_pixmap

    def _get_thumbnail_attributes(self, path: str, image: QImage) -> Dict[str, str]:
        """Return a dictionary filled with thumbnail attributes.

        Args:
            path: Path to the original image to get attributes from.
            image: QImage object to get attributes from.
        Returns:
            The generated dictionary.
        """
        return {
            KEY_URI: str(self._get_source_uri(path)),
            KEY_MTIME: str(self._get_source_mtime(path)),
            KEY_SIZE: str(os.path.getsize(path)),
            KEY_WIDTH: str(image.width()),
            KEY_HEIGHT: str(image.height()),
            KEY_SOFTWARE: f"vimiv-{vimiv.__version__}",
        }

    def _maybe_recreate_thumbnail(self, path: str, thumbnail_path: str) -> QPixmap:
        """Recreate thumbnail if image has been changed since creation.

        Args:
            path: Path to the image for which the thumbnail is created.
            thumbnail_path: Path to which the thumbnail is stored.
        Returns:
            The created QPixmap.
        """
        path_mtime = str(int(os.path.getmtime(path)))
        image = QImage(thumbnail_path)
        thumb_mtime = image.text(KEY_MTIME)
        if path_mtime == thumb_mtime:
            return QPixmap(image)
        return self._create_thumbnail(path, thumbnail_path)
