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
        pixmap: The current, possibly edited, pixmap.
    """

    def __init__(self):
        self.pixmap = QPixmap()

    def update(self, pixmap: QPixmap) -> None:
        self.pixmap = pixmap
        reload_only = True
        api.signals.pixmap_loaded.emit(pixmap, reload_only)

    @property
    def editable(self) -> bool:
        """True if the currently opened image is transformable/manipulatable."""
        return not self.pixmap.isNull()
