# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Pixmaps class to store and update the current image and the edited versions."""

from vimiv import api


class Pixmaps:
    """Class to store and update the current image and the edited versions.

    Attributes:
        _current: The current, possibly edited, pixmap.
        _original: The original unedited pixmap.
    """

    def __init__(self):
        self._current = self._original = None

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
        self._original = self._current = pixmap

    @property
    def editable(self):
        """True if the currently opened image is transformable/manipulatable."""
        return self._original is not None
