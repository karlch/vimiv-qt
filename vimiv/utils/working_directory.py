# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to take care of the current working directory.

The handler stores the current working directory and provides a method to
change it. In addition the directory and current image is monitored using
QFileSystemWatcher.

Module Attributes:
    handler: The initialized WorkingDirectoryHandler object.
"""

import logging
import time
import os
from typing import cast, List, Tuple

from PyQt5.QtCore import pyqtSignal, QFileSystemWatcher

from vimiv import api, utils, imutils
from vimiv.utils import files


class WorkingDirectoryHandler(QFileSystemWatcher):
    """Handler to store and change the current working directory.

    Signals:
        loaded: Emitted when the content for a new working directory was
                loaded.
        changed: Emitted when the content of the working directory has changed.
            arg1: List of images in the working directory.
            arg2: List of directories in the working directory.
        images_changed: Emitted when the images in the working directory have
                changed.
            arg1: List of images in the working directory.

    Class Attributes:
        WAIT_TIME: Time to wait before emitting *_changed signals.

    Attributes:
        _dir: The current working directory.
        _images: Images in the current working directory.
        _directories: Directories in the current working directory.
    """

    loaded = pyqtSignal(list, list)
    changed = pyqtSignal(list, list)
    images_changed = pyqtSignal(list)

    WAIT_TIME = 0.3

    def __init__(self):
        super().__init__()
        self._dir = None
        self._images = None
        self._directories = None
        self._processing = False

        api.settings.MONITOR_FS.changed.connect(self._on_monitor_fs_changed)
        self.directoryChanged.connect(self._reload_directory)
        self.fileChanged.connect(self._on_file_changed)
        imutils.new_image_opened.connect(self._on_new_image)

    def chdir(self, directory: str, reload_current: bool = False) -> None:
        """Change the current working directory to directory."""
        directory = os.path.abspath(directory)
        if directory != self._dir or reload_current:
            if self.directories():  # Unmonitor old directories
                self.removePaths(self.directories())
            try:
                os.chdir(directory)
                self._load_directory(directory)
                self._monitor(directory)
            except PermissionError as e:
                logging.error("%s: Cannot access '%s'", str(e), directory)

    def _monitor(self, directory: str) -> None:
        """Monitor the directory by adding it to QFileSystemWatcher."""
        if not api.settings.MONITOR_FS.value:
            return
        if not self.addPath(directory):
            logging.error("Cannot monitor %s", directory)
        else:
            logging.debug("Monitoring %s", directory)

    def _on_monitor_fs_changed(self, value: bool):
        """Start/stop monitoring when the setting changed."""
        if value:
            self._monitor(self._dir)
        else:
            logging.debug("Turning monitoring off")
            self._stop_monitoring()

    def _load_directory(self, directory: str) -> None:
        """Load supported files for new directory."""
        self._dir = directory
        self._images, self._directories = self._get_content(directory)
        self.loaded.emit(self._images, self._directories)

    @utils.slot
    def _reload_directory(self, path: str):
        """Load new supported files when directory content has changed."""
        self._process(lambda: self._emit_changes(*self._get_content(self._dir)))

    @utils.slot
    def _on_new_image(self, path: str):
        """Monitor the current image for changes."""
        if self.files():  # Clear old image
            self.removePaths(self.files())
        self.addPath(path)

    @utils.slot
    def _on_file_changed(self, path: str):
        """Emit new_image_opened signal to reload the file on changes."""
        if os.path.exists(path):  # Otherwise the path was deleted
            self._process(lambda: imutils.new_image_opened.emit(path))

    def _process(self, func):
        """Process function after waiting unless another process is running.

        This is required as images may be written in parts and loading every
        single step is neither possible nor wanted and as tools like mogrify
        from ImageMagick create temporary files which should not be loaded.

        Args:
            func: The function to call when processing.
        """
        if self._processing:
            return
        self._processing = True
        time.sleep(self.WAIT_TIME)
        func()
        self._processing = False
        api.status.update()

    def _emit_changes(self, images: List[str], directories: List[str]) -> None:
        """Emit changed signals if the content in the directory has changed.

        Args:
            images: Updated list of images in the working directory.
            directories: Updated list of directories in the working directory.
        """
        # Image filelist has changed, relevant for thumbnail and image mode
        if images != self._images:
            self.images_changed.emit(images)
        # Total filelist has changed, relevant for the library
        if images != self._images or directories != self._directories:
            self._images = images
            self._directories = directories
            self.changed.emit(images, directories)

    def _get_content(self, directory: str) -> Tuple[List[str], List[str]]:
        """Get supported content of directory.

        Returns:
            images: List of images inside the directory.
            directories: List of directories inside the directory.
        """
        show_hidden = api.settings.LIBRARY_SHOW_HIDDEN.value
        paths = files.listdir(directory, show_hidden=show_hidden)
        return files.supported(paths)


handler = cast(WorkingDirectoryHandler, None)


def init():
    """Initialize handler.

    This is required as working_directory is imported by the application but
    the QFileSystemWatcher only works appropriately once an application has
    been created.
    """
    global handler
    handler = WorkingDirectoryHandler() if handler is None else handler
