# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Widget to display a rectangle for cropping and interact with image and transform."""

from PyQt5.QtCore import Qt, QPoint, QRect, QRectF, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QApplication, QStyle, QStyleOption

from vimiv import api
from vimiv.config import styles

from .resize import ResizeLayout
from .transform_widget import TransformWidget


class CropWidget(TransformWidget):
    """Widget to display a rectangle for cropping and interact with image and transform.

    Attributes:
        _aspectratio: QSize defining the fixed ratio of width to height if any.
        _offset: Offset of a mouse drag with respect to the top-left corner.
        _selected_rect: Rectangle containing position and size relative to the image.
    """

    STYLESHEET = """
    QWidget {
        background-color: {crop.bg};
        border: {crop.border} {crop.border.color};
    }
    """

    def __init__(self, image, aspectratio=None):
        super().__init__(image)
        self.setMouseTracking(True)

        self._aspectratio = aspectratio if aspectratio is not None else QSize()
        self._offset = QPoint(0, 0)

        scene_rect = self.image.sceneRect()
        self._selected_rect = QRectF(scene_rect.topLeft(), scene_rect.center())

        styles.apply(self)
        self.update_geometry()
        self.show()

        ResizeLayout(self, fixed_aspectratio=aspectratio is not None)

    @property
    def moving(self) -> bool:
        """True if the widget is currently being dragged."""
        cursor = QApplication.overrideCursor()
        return cursor is not None and cursor.shape() == Qt.ClosedHandCursor

    def crop_rect(self) -> QRect:
        """Rectangle of the image that would currently be cropped."""
        return (self._selected_rect & self.image.sceneRect()).toRect()

    def update_geometry(self):
        """Update geometry to keep size and position relative to the image."""
        geometry = self.image.mapFromScene(self._selected_rect).boundingRect()
        self.setGeometry(geometry)
        api.status.update("crop widget geometry changed")

    def update_selected_rect(self):
        self._selected_rect = self.image.mapToScene(self.geometry()).boundingRect()

    def status_info(self) -> str:
        """Rectangle geometry of the image that would currently be cropped."""
        rect = self.crop_rect()
        return f"crop: {rect.width()}x{rect.height()}+{rect.x()}+{rect.y()}"

    def resizeEvent(self, _event):
        """Update size fractions ensuring aspectratio."""
        if self._aspectratio.isValid():
            size = QSize(self._aspectratio)
            size.scale(self.size(), Qt.KeepAspectRatio)
            self.resize(size)
        self.update_selected_rect()
        api.status.update("crop widget resized")

    def leave(self, accept: bool = False):
        """Override leave to crop the image on accept."""
        if accept:
            self.transform.crop(self.crop_rect())
        super().leave(accept)

    def mousePressEvent(self, event):
        """Start dragging the widget if we click within it."""
        if self.geometry().contains(event.pos() + self.pos()):
            self._offset = event.pos()
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        """Move the widget if it is currently being dragged.

        We use the global position in order to avoid a flickering motion. Once the mouse
        is outside the parent widget, the movement is stopped.
        """
        if self.moving:
            event_pos = event.globalPos()
            origin = self.image.mapToGlobal(QPoint(0, 0))
            if not self.image.geometry().contains(event_pos - origin):
                return
            point = event_pos - origin - self._offset
            self.move(point)
            self.update_selected_rect()
            api.status.update("crop widget moved")

    def mouseReleaseEvent(self, _event):
        """Stop dragging the widget."""
        QApplication.restoreOverrideCursor()

    def paintEvent(self, _event):
        """Paint a simple rectangle according to the stylesheet."""
        opt = QStyleOption()
        opt.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, painter, self)
