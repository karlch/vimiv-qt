# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Widget to display a grid for straightening and interact with image and transform."""

import enum
import functools

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QWidget, QStyleOption

from vimiv import api
from vimiv.imutils import imtransform
from vimiv.config import styles


class Direction(enum.IntEnum):
    """Enum defining valid rotation directions."""

    Clockwise = 0
    CounterClockwise = 1


class StraightenWidget(QWidget):
    """Widget to display a grid for straightening and interact with image and transform.

    The grid is a visual helper for the user to straighten the image. An interaction
    with the imtransform module to apply the transformations and the image widget to
    display the transformation is performed with this class acting as man-in-the-middle.

    Attributes:
        bindings: Dictionary of keybindings required for straightening.
    """

    LINES = (
        (0.25, Qt.DashLine, 2),
        (0.5, Qt.SolidLine, 4),
        (0.75, Qt.DashLine, 2),
    )

    def __init__(self, image):
        super().__init__(parent=image)
        self.setObjectName(self.__class__.__qualname__)
        self.setWindowFlags(Qt.SubWindow)
        self.setFocus()

        self.bindings = {
            Qt.Key_Escape: self.leave,
            Qt.Key_Return: functools.partial(self.leave, accept=True),
            Qt.Key_L: functools.partial(self.rotate, direction=Direction.Clockwise),
            Qt.Key_H: functools.partial(
                self.rotate, direction=Direction.CounterClockwise
            ),
        }
        self.color = QColor(styles.get("image.straighten.color"))
        self.transform = imtransform.Transform.instance
        self.previous_matrix = self.transform.matrix
        self.total_angle = 0

        image.resized.connect(self.update_geometry)
        self.update_geometry()
        self.show()

    def leave(self, accept: bool = False):
        """Leave the straighten widget for image mode.

        Args:
            accept: If True, keep the straightening as transformation.
        """
        if not accept:
            self.transform.setMatrix(*self.previous_matrix)
            self.transform.apply()
        self.parent().setFocus()  # type: ignore

    def rotate(self, direction: Direction):
        """Rotate the image in the given direction to perform straightening.

        The heavy lifting is done by transform, this function only provides the binding
        link to user-interaction and the GUI.
        """
        angle = 1 if direction == Direction.Clockwise else -1
        self.transform.setMatrix(*self.previous_matrix)  # Reset any performed changes
        self.total_angle += angle
        self.transform.straighten(angle=self.total_angle)
        self.update_geometry()

    def update_geometry(self):
        """Update geometry of the grid to overlay the image."""
        image_size = self.parent().sceneRect()
        width = min(
            int(image_size.width() * self.parent().zoom_level), self.parent().width()
        )
        height = min(
            int(image_size.height() * self.parent().zoom_level), self.parent().height()
        )
        self.setFixedSize(width, height)
        x = (self.parent().width() - width) // 2
        y = (self.parent().height() - height) // 2
        self.move(x, y)

    def keyPressEvent(self, event):
        """Prefer custom bindings, fall back to the parent (image) widget."""
        binding = self.bindings.get(event.key())
        if binding is not None:
            api.status.clear("straighten binding")
            binding()
            api.status.update("straighten binding")
        else:
            self.parent().keyPressEvent(event)

    def paintEvent(self, _event):
        """Paint a grid of helper lines."""
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        pen = QPen(self.color)
        for fraction, style, width in self.LINES:
            pen.setStyle(style)
            pen.setWidth(width)
            painter.setPen(pen)
            x_fraction = int(self.width() * fraction)
            y_fraction = int(self.height() * fraction)
            painter.drawLine(0, y_fraction, self.width(), y_fraction)
            painter.drawLine(x_fraction, 0, x_fraction, self.height())

    def focusOutEvent(self, event):
        """Delete the widget when focusing out."""
        self.deleteLater()
        super().focusOutEvent(event)
