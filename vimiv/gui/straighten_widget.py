# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Widget to display a grid for straightening and interact with image and transform."""

import functools

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QStyleOption

from vimiv import utils
from vimiv.config import styles

from .transform_widget import TransformWidget


class StraightenWidget(TransformWidget):
    """Widget to display a grid for straightening and interact with image and transform.

    The grid is a visual helper for the user to straighten the image. An interaction
    with the imtransform module to apply the transformations and the image widget to
    display the transformation is performed with this class acting as man-in-the-middle.

    Attributes:
        color: Color of the grid lines.
        angle: Current rotation angle in degrees.

        _init_size: Size of the initially unstraightened pixmap.
    """

    LINES = (
        (0.25, Qt.DashLine, 2),
        (0.5, Qt.SolidLine, 4),
        (0.75, Qt.DashLine, 2),
    )

    def __init__(self, image):
        super().__init__(image)
        self._add_rotate_binding("l", ">", angle=0.2)
        self._add_rotate_binding("L", angle=1.0)
        self._add_rotate_binding("h", "<", counter_clockwise=True, angle=0.2)
        self._add_rotate_binding("H", counter_clockwise=True, angle=1.0)

        self.color = QColor(styles.get("image.straighten.color"))
        self.angle = 0.0
        self._init_size = self.transform.size

    def _add_rotate_binding(
        self, *keys: str, counter_clockwise: bool = False, angle: float
    ) -> None:
        """Add keybindings for the rotate command.

        Args:
            keys: Tuple of keys to bind to this command.
            counter_clockwise: True for rotating counter clockwise.
            angle: Angle in degrees by which the command rotates.
        """
        func = functools.partial(
            self.rotate, counter_clockwise=counter_clockwise, angle=angle
        )
        for key in keys:
            self.bindings[(key,)] = func

    def rotate(self, *, counter_clockwise: bool = False, angle: float = 1.0):
        """Rotate the image in the given direction to perform straightening.

        The heavy lifting is done by transform, this function only provides the binding
        link to user-interaction and the GUI.
        """
        angle = -angle if counter_clockwise else angle
        self.angle += angle
        self._perform_rotate()

    @utils.throttled(delay_ms=0)
    def _perform_rotate(self):
        """Throttled implementation of the actual rotate.

        The throttling keeps the UI responsive and stops the CPU from going wild when
        holding down any of the rotate keys.
        """
        self.reset_transformations()
        self.transform.straighten(angle=self.angle, original_size=self._init_size)
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

    def status_info(self):
        """Display current rotation angle in the status bar."""
        return f"angle: {self.angle:+.1f}°"

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
