# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Pixmaps class to store and update the current image and the edited versions."""

from PyQt5.QtGui import QPixmap

from vimiv import api


class Pixmaps:
    """Class to store and update the current image and the edited versions.

    Attributes:
        _current: The current possibly transformed and manipulated pixmap.
        _original: The original unedited pixmap.
        _transformed: The possibly transformed but unmanipulated pixmap.
    """

    def __init__(self):
        self._current = self._original = self._transformed = None

    @property
    def current(self):
        """The currently displayed pixmap.

        Upon setting a signal to update the image shown is emitted.
        """
        return self._current

    @current.setter
    def current(self, pixmap):
        self._current = pixmap
        reload_only = True
        api.signals.pixmap_loaded.emit(pixmap, reload_only)

    @property
    def original(self):
        """Original pixmap without any transformation or manipulations.

        Upon setting all edited pixmaps are reset as well.
        """
        return self._original

    @original.setter
    def original(self, pixmap) -> None:
        self._original = self._transformed = self._current = pixmap

    @property
    def transformed(self):
        """Transformed pixmap without any manipulations applied.

        Upon setting the current pixmap gets updated and shown.
        """
        return self._transformed

    @transformed.setter
    def transformed(self, pixmap):
        self._transformed = pixmap
        self.current = pixmap

    @property
    def editable(self):
        """True if the currently opened image is transformable/manipulatable."""
        return isinstance(self._original, QPixmap)
