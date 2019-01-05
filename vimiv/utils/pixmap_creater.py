# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Create simple versions of QPixmap."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter

from vimiv.config import styles


def default_thumbnail():
    """Return QIcon to display for default thumbnails."""
    color = styles.get("thumbnail.default.bg")
    return thumbnail(color)


def error_thumbnail():
    """Return QIcon to display for failed thumbnails."""
    color = styles.get("thumbnail.error.bg")
    return thumbnail(color)


def thumbnail(colorname):
    """Return QIcon of size 256 filled with one color and a frame.

    Args:
        colorname: Color in hex format.
    """
    pixmap = QPixmap(256, 256)
    frame_color = styles.get("thumbnail.frame.fg")
    _draw(pixmap, colorname, 10, frame_color)
    return pixmap


def _draw(pixmap, colorname, frame_size, frame_colorname):
    """Draw pixmap with frame and inner color.

    Args:
        pixmap: QPixmap to draw on.
        colorname: Name of the inner color in hex format.
        frame_size: Size of the frame to draw in px.
        frame-colorname: Name of the frame color in hex format.
    """
    painter = QPainter(pixmap)
    painter.setPen(Qt.NoPen)
    color = QColor(0, 0, 0)
    # Frame
    color.setNamedColor(frame_colorname)
    painter.setBrush(color)
    painter.drawRect(pixmap.rect())
    # Inner
    color.setNamedColor(colorname)
    painter.setBrush(color)
    x = y = frame_size
    width = height = pixmap.width() - 2 * frame_size
    painter.drawRect(x, y, width, height)
