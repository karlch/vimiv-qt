# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Deals with changing and storing paths to currently loaded images.

Module Attributes:
    signals: Class with the Qt signals for other parts to connect to.
    _storage: Created Storage class with the loaded paths.

Signals:
    new_image: Emitted if the path of the current image has changed.
"""

import os
from random import shuffle

from vimiv.commands import commands
from vimiv.config import keybindings, settings
from vimiv.gui import statusbar
from vimiv.imutils.imcommunicate import signals
from vimiv.utils import objreg, slideshow, files


class Storage():
    """Store and manipulate paths to images.

    Attributes:
        _paths: List of image paths.
        _index: Index of the currently displayed image in the _paths list.
    """

    @objreg.register("imstorage")
    def __init__(self):
        self._paths = []
        self._index = 0
        slides = slideshow.Slideshow()
        slides.next_im.connect(self._on_slideshow_event)
        signals.update_index.connect(self._on_update_index)
        signals.update_path.connect(self._on_update_path)
        signals.update_paths.connect(self._on_update_paths)

    @keybindings.add("n", "next", mode="image")
    @commands.register(instance="imstorage", count=1)
    def next(self, count):
        """Goto to next image.

        Args:
            count: How many images to jump forwards.
        """
        if self._paths:
            self._set_index((self._index + count) % len(self._paths))
            signals.path_loaded.emit(self.current())

    @keybindings.add("p", "prev", mode="image")
    @commands.register(instance="imstorage", count=1)
    def prev(self, count):
        """Goto to previous image.

        Args:
            count: How many images to jump backwards.
        """
        if self._paths:
            self._set_index((self._index - count) % len(self._paths))
            signals.path_loaded.emit(self.current())

    @keybindings.add("G", "goto -1", mode="image")
    @keybindings.add("gg", "goto 1", mode="image")
    @commands.argument("index", type=int)
    @commands.register(instance="imstorage", mode="image", count=0)
    def goto(self, index, count):
        """Goto image at index.

        Args:
            index: Index of the image to select of no count is given.
                -1 is the last image.
        """
        index = count if count else index
        self._set_index(index % (len(self._paths) + 1) - 1)
        signals.path_loaded.emit(self.current())

    @statusbar.module("{abspath}", instance="imstorage")
    def current(self):
        """Return the path to the current image or None."""
        if self._paths:
            return self._paths[self._index]
        return ""

    @statusbar.module("{basename}", instance="imstorage")
    def basename(self):
        """Return the basename of the currently selected image."""
        return os.path.basename(self.current())

    @statusbar.module("{index}", instance="imstorage")
    def index(self):
        """Return index formatted as zero prepended string."""
        if self._paths:
            return str(self._index + 1).zfill(len(self.total()))
        return "0"

    @statusbar.module("{total}", instance="imstorage")
    def total(self):
        """Return total amount of paths as string."""
        return str(len(self._paths))

    def _on_slideshow_event(self):
        self.next(1)

    def _on_update_index(self, index):
        self.goto(index, 0)

    def _on_update_path(self, path):
        if path in self._paths:
            self.goto(self._paths.index(path) + 1, 0)
        else:
            self._load_single(path)

    def _on_update_paths(self, paths, index):
        """Load new paths into storage.

        Args:
            paths: List of paths to load.
            index: Index of the path to display.
        """
        paths = [os.path.abspath(path) for path in paths]
        directory = os.path.dirname(paths[0])
        signals.maybe_update_library.emit(directory)
        # Populate list of paths in same directory for single path
        if len(paths) == 1:
            self._load_single(paths[0])
        else:
            self._paths = paths
            if settings.get_value("shuffle"):
                shuffle(self._paths)
            self._set_index(index)
            signals.paths_loaded.emit(self._paths)
            signals.path_loaded.emit(self._paths[self._index])

    def _load_single(self, path):
        """Populate list of paths in same directory for single path."""
        directory = os.path.dirname(path)
        self._paths, _ = files.get_supported(files.ls(directory))
        if settings.get_value("shuffle"):
            shuffle(self._paths)
        self._set_index(self._paths.index(path))
        signals.paths_loaded.emit(self._paths)
        signals.path_loaded.emit(self._paths[self._index])

    def _set_index(self, index):
        signals.maybe_write_file.emit(self.current())
        self._index = index


def current():
    """Convenience function to get name of current image.

    Return:
        abspath to the current image.
    """
    storage = objreg.get("imstorage")
    return storage.current()
