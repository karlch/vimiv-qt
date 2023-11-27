# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Utilities to make widgets nicely resizable using QSizeGrips."""

from vimiv.qt.core import Qt, Align
from vimiv.qt.widgets import QApplication, QSizeGrip, QGridLayout


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
        self._override_cursor = (
            Qt.CursorShape.SizeVerCursor if vertical else Qt.CursorShape.SizeHorCursor
        )
        self.destroyed.connect(QApplication.restoreOverrideCursor)

    @property
    def vertical(self):
        return self._override_cursor == Qt.CursorShape.SizeVerCursor

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
        self.addWidget(QSizeGrip(parent), 0, 0, Align.Left | Align.Top)
        self.addWidget(QSizeGrip(parent), 2, 0, Align.Left | Align.Bottom)
        self.addWidget(QSizeGrip(parent), 0, 2, Align.Right | Align.Top)
        self.addWidget(QSizeGrip(parent), 2, 2, Align.Right | Align.Bottom)

    def _add_edges(self, parent):
        """Add one QSizeGrip to each edge, constrained to the corresponding axis."""
        self.addWidget(
            SizeGrip1D(parent, vertical=True), 0, 1, Align.Center | Align.Top
        )
        self.addWidget(
            SizeGrip1D(parent, vertical=True), 2, 1, Align.Center | Align.Bottom
        )
        self.addWidget(
            SizeGrip1D(parent, vertical=False), 1, 0, Align.Left | Align.Center
        )
        self.addWidget(
            SizeGrip1D(parent, vertical=False), 1, 2, Align.Right | Align.Center
        )
