# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Deals with changing and storing paths to currently loaded images.

Module Attributes:
    signals: Class with the Qt signals for other parts to connect to.
    _storage: Created Storage class with the loaded paths.

Signals:
    new_image: Emitted if the path of the current image has changed.
"""

import os

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.imutils.imcommunicate import signals
from vimiv.utils import objreg, slideshow, files


class Storage():
    """Store and manipulate paths to images.

    Attributes:
        _paths: List of image paths.
        _index: Index of the currently displayed image in the _paths list.
    """

    @objreg.register("impaths")
    def __init__(self):
        self._paths = []
        self._index = 0
        slides = slideshow.Slideshow()
        slides.next_im.connect(self._on_slideshow_event)
        signals.update_index.connect(self._on_update_index)
        signals.update_path.connect(self._on_update_path)
        signals.update_paths.connect(self._on_update_paths)

    @keybindings.add("n", "next", mode="image")
    @commands.register(instance="impaths", count=1)
    def next(self, count):
        """Goto to next image.

        Args:
            count: How many images to jump forwards.
        """
        if self._paths:
            self._index = (self._index + count) % len(self._paths)
            signals.path_loaded.emit(self.current())

    @keybindings.add("p", "prev", mode="image")
    @commands.register(instance="impaths", count=1)
    def prev(self, count):
        """Goto to previous image.

        Args:
            count: How many images to jump backwards.
        """
        if self._paths:
            self._index = (self._index - count) % len(self._paths)
            signals.path_loaded.emit(self.current())

    @keybindings.add("G", "goto -1", mode="image")
    @keybindings.add("gg", "goto 1", mode="image")
    @commands.argument("index", type=int)
    @commands.register(instance="impaths", mode="image", count=0)
    def goto(self, index, count):
        """Goto image at index.

        Args:
            index: Index of the image to select of no count is given.
                -1 is the last image.
        """
        index = count if count else index
        self._index = index % (len(self._paths) + 1) - 1
        signals.path_loaded.emit(self.current())

    @statusbar.module("{abspath}", instance="impaths")
    def current(self):
        """Return the path to the current image or None."""
        if self._paths:
            return self._paths[self._index]
        return ""

    @statusbar.module("{basename}", instance="impaths")
    def basename(self):
        """Return the basename of the currently selected image."""
        return os.path.basename(self.current())

    @statusbar.module("{index}", instance="impaths")
    def index(self):
        """Return index formatted as zero prepended string."""
        if self._paths:
            return str(self._index + 1).zfill(len(self.total()))
        return "0"

    @statusbar.module("{total}", instance="impaths")
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
        paths = [os.path.abspath(path) for path in paths]
        directory = os.path.dirname(paths[0])
        # TODO update library
        if directory != os.getcwd():
            os.chdir(directory)
        # Populate list of paths in same directory for single path
        if len(paths) == 1:
            self._load_single(paths[0])
        else:
            self._paths = paths
            self._index = index
            signals.paths_loaded.emit(self._paths)
            signals.path_loaded.emit(self._paths[self._index])

    def _load_single(self, path):
        """Populate list of paths in same directory for single path."""
        directory = os.path.dirname(path)
        self._paths, _ = files.get_supported(files.ls(directory))
        self._index = self._paths.index(path)
        signals.paths_loaded.emit(self._paths)
        signals.path_loaded.emit(self._paths[self._index])
