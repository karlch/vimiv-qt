# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
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

from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, Qt
from PyQt5.QtGui import QPixmap, QImageReader, QImage

import vimiv
from vimiv.utils import xdg, pixmap_creater


KEY_URI = 'Thumb::URI'
KEY_MTIME = 'Thumb::MTime'
KEY_SIZE = 'Thumb::Size'
KEY_WIDTH = 'Thumb::Image::Width'
KEY_HEIGHT = 'Thumb::Image::Height'
KEY_SOFTWARE = 'Software'


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

    created = pyqtSignal(int, QPixmap)
    pool = QThreadPool.globalInstance()

    def __init__(self, large=True):
        super().__init__()
        self.large = large

        directory = os.path.join(xdg.get_user_cache_dir(), "thumbnails")
        self.directory = os.path.join(directory, "large") if large \
            else os.path.join(directory, "normal")
        self.fail_directory = \
            os.path.join(directory, "fail", "vimiv-%s" % (vimiv.__version__))
        os.makedirs(self.directory, exist_ok=True)
        os.makedirs(self.fail_directory, exist_ok=True)
        self.fail_pixmap = pixmap_creater.error_thumbnail()

    def create_thumbnails_async(self, paths):
        """Start ThumbnailsAsyncCreator to create thumbnails.

        Args:
            paths: Paths to create thumbnails for.
        """
        self.pool.clear()
        async_creator = ThumbnailsAsyncCreator(paths, self)
        self.pool.start(async_creator)


class ThumbnailsAsyncCreator(QRunnable):
    """Create thumbnails asynchronously.

    Adds one ThumbnailCreator runnable to the thread pool for each thumbnail
    and starts it.

    Attributes:
        _paths: List of paths to original images.
        _manager: The ThumbnailManager object used for callback.
    """

    _pool = QThreadPool.globalInstance()

    def __init__(self, paths, manager):
        super().__init__()
        self._paths = paths
        self._manager = manager

    def run(self):
        """Start ThumbnailCreator for each path."""
        for i, path in enumerate(self._paths):
            creator = ThumbnailCreator(i, path, self._manager)
            self._pool.start(creator)


class ThumbnailCreator(QRunnable):
    """Create thumbnail for one path.

    Implements freedesktop's thumbnail managing standard:
    https://specifications.freedesktop.org/thumbnail-spec/thumbnail-spec-latest.html

    Attributes:
        _index: Index of the thumbnail in the thumbnail widget.
        _path: Path to the original image.
        _manager: The ThumbnailManager object used for callback.
    """

    def __init__(self, index, path, manager):
        super().__init__()
        self._index = index
        self._path = path
        self._manager = manager

    def run(self):
        """Create thumbnail and emit the managers created signal."""
        thumbnail_path = self._get_thumbnail_path(self._path)
        if os.path.exists(thumbnail_path):
            pixmap = self._maybe_recreate_thumbnail(self._path, thumbnail_path)
        else:
            pixmap = self._create_thumbnail(self._path, thumbnail_path)
            # Additional safety net
            pixmap = pixmap if pixmap else self._manager.fail_pixmap
        self._manager.created.emit(self._index, pixmap)

    def _get_thumbnail_path(self, path):
        filename = self._get_thumbnail_filename(path)
        return os.path.join(self._manager.directory, filename)

    @staticmethod
    def _get_source_uri(path):
        return "file://" + os.path.abspath(os.path.expanduser(path))

    def _get_thumbnail_filename(self, path):
        uri = self._get_source_uri(path)
        return hashlib.md5(bytes(uri, "UTF-8")).hexdigest() + ".png"

    @staticmethod
    def _get_source_mtime(path):
        return int(os.path.getmtime(path))

    def _create_thumbnail(self, path, thumbnail_path):
        """Create thumbnail for an image.

        Args:
            path: Path to the image for which the thumbnail is created.
            thumbnail_path: Path to which the thumbnail is stored.
        Return:
            The created QPixmap.
        """
        # Cannot access source; create neither thumbnail nor fail file
        if not os.access(path, os.R_OK):
            return False
        size = 256 if self._manager.large else 128
        reader = QImageReader(path)
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
            handle, tmp_filename = \
                tempfile.mkstemp(dir=self._manager.directory)
            os.close(handle)
            os.chmod(tmp_filename, 0o600)
            image.save(tmp_filename, format="png")
            os.replace(tmp_filename, thumbnail_path)
            return QPixmap(image)
        return self._manager.fail_pixmap

    def _get_thumbnail_attributes(self, path, image):
        """Return a dictionary filled with thumbnail attributes.

        Args:
            path: Path to the original image to get attributes from.
            image: QImage object to get attributes from.
        Return:
            The generated dictionary.
        """
        return {
            KEY_URI: str(self._get_source_uri(path)),
            KEY_MTIME: str(self._get_source_mtime(path)),
            KEY_SIZE: str(os.path.getsize(path)),
            KEY_WIDTH: str(image.width()),
            KEY_HEIGHT: str(image.height()),
            KEY_SOFTWARE: "vimiv-%s" % (vimiv.__version__),
        }

    def _maybe_recreate_thumbnail(self, path, thumbnail_path):
        """Recreate thumbnail if image has been changed since creation.

        Args:
            path: Path to the image for which the thumbnail is created.
            thumbnail_path: Path to which the thumbnail is stored.
        Return:
            The created QPixmap.
        """
        path_mtime = str(int(os.path.getmtime(path)))
        image = QImage(thumbnail_path)
        thumb_mtime = image.text(KEY_MTIME)
        if path_mtime == thumb_mtime:
            return QPixmap(image)
        return self._create_thumbnail(path, thumbnail_path)
