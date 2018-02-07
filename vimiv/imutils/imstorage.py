# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Deals with changing and storing paths to currently loaded images."""

import os
from random import shuffle

from PyQt5.QtCore import pyqtSlot, QObject

from vimiv import app
from vimiv.commands import commands
from vimiv.config import keybindings, settings
from vimiv.gui import statusbar
from vimiv.imutils import imsignals
from vimiv.utils import objreg, files


class Storage(QObject):
    """Store and move between paths to images.

    Attributes:
        _paths: List of image paths.
        _index: Index of the currently displayed image in the _paths list.
    """

    @objreg.register("imstorage")
    def __init__(self):
        super().__init__()
        self._paths = []
        self._index = 0
        slideshow = objreg.get("slideshow")
        slideshow.next_im.connect(self._on_slideshow_event)
        trash_manager = objreg.get("trash-manager")
        trash_manager.path_removed.connect(self._on_path_removed)
        trash_manager.path_restored.connect(self._on_path_restored)
        imsignals.connect(self._on_update_index, "update_index")
        imsignals.connect(self._on_update_path, "update_path")
        imsignals.connect(self._on_update_paths, "update_paths")

    @keybindings.add("n", "next", mode="image")
    @commands.register(instance="imstorage", count=1)
    def next(self, count):
        """Select next image.

        **count:** multiplier
        """
        if self._paths:
            self._set_index((self._index + count) % len(self._paths))
            imsignals.emit("path_loaded", self.current())

    @keybindings.add("p", "prev", mode="image")
    @commands.register(instance="imstorage", count=1)
    def prev(self, count):
        """Select previous image.

        **count:** multiplier
        """
        if self._paths:
            self._set_index((self._index - count) % len(self._paths))
            imsignals.emit("path_loaded", self.current())

    @keybindings.add("G", "goto -1", mode="image")
    @keybindings.add("gg", "goto 1", mode="image")
    @commands.argument("index", type=int)
    @commands.register(instance="imstorage", mode="image", count=0)
    def goto(self, index, count):
        """Select specific image in current filelist.

        **syntax:** ``:goto index``

        positional arguments:
            * index: Number of the image to select.

        .. hint:: -1 is the last image.

        **count:** Select [count]th image instead.
        """
        index = count if count else index
        self._set_index(index % (len(self._paths) + 1) - 1)
        imsignals.emit("path_loaded", self.current())

    @statusbar.module("{abspath}", instance="imstorage")
    def current(self):
        """Absolute path to the current image."""
        if self._paths:
            return self._paths[self._index]
        return ""

    @statusbar.module("{basename}", instance="imstorage")
    def basename(self):
        """Basename of the current image."""
        return os.path.basename(self.current())

    @statusbar.module("{index}", instance="imstorage")
    def index(self):
        """Index of the current image."""
        if self._paths:
            return str(self._index + 1).zfill(len(self.total()))
        return "0"

    @statusbar.module("{total}", instance="imstorage")
    def total(self):
        """Total amount of images."""
        return str(len(self._paths))

    def pathlist(self):
        """Return the currently loaded list of paths."""
        return self._paths

    @pyqtSlot()
    def _on_slideshow_event(self):
        self.next(1)

    @pyqtSlot(int)
    def _on_update_index(self, index):
        self.goto(index, 0)

    @pyqtSlot(str)
    def _on_update_path(self, path):
        if path in self._paths:
            self.goto(self._paths.index(path) + 1, 0)
        else:
            self._load_single(path)

    @pyqtSlot(list, int)
    def _on_update_paths(self, paths, index):
        """Load new paths into storage.

        Args:
            paths: List of paths to load.
            index: Index of the path to display.
        """
        paths = [os.path.abspath(path) for path in paths]
        directory = os.path.dirname(paths[0])
        imsignals.emit("maybe_update_library", directory)
        # Populate list of paths in same directory for single path
        if len(paths) == 1:
            self._load_single(paths[0])
        else:
            self._set_index(index)
            self._paths = paths
            if settings.get_value("shuffle"):
                shuffle(self._paths)
            imsignals.emit("paths_loaded", self._paths)
            imsignals.emit("path_loaded", self.current())

    def _load_single(self, path):
        """Populate list of paths in same directory for single path."""
        directory = os.path.dirname(path)
        paths, _ = files.get_supported(files.ls(directory))
        if settings.get_value("shuffle"):
            shuffle(paths)
        self._set_index(paths.index(path))
        self._paths = paths  # Must update after index for maybe_write
        imsignals.emit("paths_loaded", self._paths)
        imsignals.emit("path_loaded", self.current())

    def _set_index(self, index):
        imsignals.emit("maybe_write_file", self.current())
        self._index = index

    @pyqtSlot(str)
    def _on_path_removed(self, path):
        """Remove path from filelist and reload paths if necessary."""
        if path in self._paths:
            path_index = self._paths.index(path)
            current_path = self.current()
            self._paths.remove(path)
            # Select parent directory in library if no more paths are available
            if not self._paths:
                # TODO clear the image displayed
                app.open("..")
            # Move to next image available if the current path was removed
            elif path == current_path:
                self._index = min(path_index, len(self._paths) - 1)
                imsignals.emit("path_loaded", self.current())
            # Make sure the current image is still selected
            else:
                self._set_index(self._paths.index(current_path))

    @pyqtSlot(str)
    def _on_path_restored(self, path):
        """Restore path to filelist and reload paths if necessary."""
        if os.path.dirname(path) == os.path.dirname(self.current()):
            current_path = self.current()
            self._paths.append(path)
            self._paths.sort()
            self._set_index(self._paths.index(current_path))


def current():
    """Convenience function to get name of current image.

    Return:
        abspath to the current image.
    """
    storage = objreg.get("imstorage")
    return storage.current()
