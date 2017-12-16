# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Deals with changing and storing paths to currently loaded images.

Module Attributes:
    signals: Class with the Qt signals for other parts to connect to.
    _storage: Created Storage class with the loaded paths.

Signals:
    new_image: Emitted if the path of the current image has changed.
"""

import os

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.utils import objreg


class Signals(QObject):
    """Class to store the qt signals for others to connect to."""

    new_image = pyqtSignal(str)


signals = Signals()


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

    @keybindings.add("next", "n", "image")
    @commands.register(instance="impaths")
    def next(self):
        """Display the next currently loaded image."""
        if self._paths:
            self._index = (self._index + 1) % len(self._paths)
            signals.new_image.emit(self.current())

    @keybindings.add("prev", "p", "image")
    @commands.register(instance="impaths")
    def prev(self):
        """Display the previous loaded image."""
        if self._paths:
            self._index = (self._index - 1) % len(self._paths)
            signals.new_image.emit(self.current())

    @keybindings.add("goto --last", "G", "image")
    @keybindings.add("goto", "g", "image")
    @commands.argument("--last", action="store_true")
    @commands.register(instance="impaths")
    def goto(self, last=False):
        """Display a specific loaded image.

        Args:
            last: Select the last image.
        """
        self._index = len(self._paths) - 1 if last else 0
        signals.new_image.emit(self.current())

    def current(self):
        """Return the path to the current image or None."""
        if self._paths:
            return self._paths[self._index]
        return ""

    def load(self, paths, index=0):
        """Load paths into storage.

        Args:
            paths: List of paths to store.
            index: Index of the image to select in paths.
        """
        self._paths = paths
        self._index = index
        signals.new_image.emit(self.current())

    def index(self):
        """Return index formatted as zero prepended string."""
        if self._paths:
            return str(self._index + 1).zfill(len(self.total()))
        return "0"

    def total(self):
        """Return total amount of paths as string."""
        return str(len(self._paths))


_storage = Storage()


def load(paths, index=0):
    """Load paths into the image path storage."""
    _storage.load(paths, index)


@statusbar.module("{abspath}")
def current():
    """Return the absolute path of the currently selected image."""
    return _storage.current()


@statusbar.module("{basename}")
def _basename_current():
    """Return the basename of the currently selected image."""
    return os.path.basename(current())


@statusbar.module("{index}")
def _index():
    """Return the index of the currently selected image."""
    return _storage.index()


@statusbar.module("{total}")
def _total():
    """Return the total amount of loaded images."""
    return _storage.total()
