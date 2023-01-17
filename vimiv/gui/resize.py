# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utilities to make widgets nicely resizable using QSizeGrips."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QSizeGrip, QGridLayout


class SizeGrip1D(QSizeGrip):
    """Size grip that constrains resizing to one axis.

    Attributes:
        _minimum_size: Minimum size of the parent widget before constraining.
        _maximum_size: Minimum size of the parent widget before constraining.
        _override_cursor: Cursor to display when over the size grip.
    """

    def __init__(self, parent, *, vertical: bool):
        super().__init__(parent)
        self._minimum_size = parent.minimumSize()
        self._maximum_size = parent.maximumSize()
        self._override_cursor = Qt.SizeVerCursor if vertical else Qt.SizeHorCursor
        self.destroyed.connect(QApplication.restoreOverrideCursor)

    @property
    def vertical(self):
        return self._override_cursor == Qt.SizeVerCursor

    def mousePressEvent(self, event):
        """Constrain one axis when pressing the mouse."""
        if self.vertical:
            self.parent().setFixedWidth(self.parent().width())
        else:
            self.parent().setFixedHeight(self.parent().height())
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Reset the constraint when releasing the mouse."""
        self.parent().setMinimumSize(self._minimum_size)
        self.parent().setMaximumSize(self._maximum_size)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        QApplication.setOverrideCursor(self._override_cursor)
        super().enterEvent(event)

    def leaveEvent(self, event):
        QApplication.restoreOverrideCursor()
        super().leaveEvent(event)


class ResizeLayout(QGridLayout):
    """Grid layout initialized with size grips for resizing."""

    def __init__(self, parent, *, fixed_aspectratio=False):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self._add_corners(parent)
        if not fixed_aspectratio:
            self._add_edges(parent)

    def _add_corners(self, parent):
        """Add one QSizeGrip to each corner."""
        self.addWidget(QSizeGrip(parent), 0, 0, Qt.AlignLeft | Qt.AlignTop)
        self.addWidget(QSizeGrip(parent), 2, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.addWidget(QSizeGrip(parent), 0, 2, Qt.AlignRight | Qt.AlignTop)
        self.addWidget(QSizeGrip(parent), 2, 2, Qt.AlignRight | Qt.AlignBottom)

    def _add_edges(self, parent):
        """Add one QSizeGrip to each edge, constrained to the corresponding axis."""
        self.addWidget(
            SizeGrip1D(parent, vertical=True), 0, 1, Qt.AlignCenter | Qt.AlignTop
        )
        self.addWidget(
            SizeGrip1D(parent, vertical=True), 2, 1, Qt.AlignCenter | Qt.AlignBottom
        )
        self.addWidget(
            SizeGrip1D(parent, vertical=False), 1, 0, Qt.AlignLeft | Qt.AlignCenter
        )
        self.addWidget(
            SizeGrip1D(parent, vertical=False), 1, 2, Qt.AlignRight | Qt.AlignCenter
        )
