# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Pixmaps class to store and update the current image and the edited versions."""

from PyQt5.QtGui import QPixmap

from vimiv import api


class CurrentPixmap:
    """Class to store and retrieve the current pixmap for editing, saving and so forth.

    Attributes:
        _pixmap: The current, possibly edited, pixmap.
    """

    def __init__(self):
        self._pixmap = QPixmap()

    def get(self) -> QPixmap:
        return self._pixmap

    def update(self, pixmap: QPixmap, *, reload_only: bool) -> None:
        self._pixmap = pixmap
        api.signals.pixmap_loaded.emit(pixmap, reload_only)

    @property
    def editable(self) -> bool:
        """True if the currently opened image is transformable/manipulatable."""
        return not self._pixmap.isNull()

    def clear(self) -> None:
        self._pixmap = QPixmap()
