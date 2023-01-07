# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Storage class for the current pixmap."""

from vimiv.qt.gui import QPixmap


class CurrentPixmap:
    """Storage class for the current pixmap shared between various edit-related classes.

    We do not use a simple QPixmap as we would have to update various attributes of the
    classes that wish to access the pixmap simultaneously. Like this they can all share
    this class and access the pixmap through it.

    Attributes:
        pixmap: The current, possibly edited, pixmap.
    """

    def __init__(self):
        self.pixmap = QPixmap()

    @property
    def editable(self) -> bool:
        """True if the currently opened image is transformable/manipulatable."""
        return not self.pixmap.isNull()
