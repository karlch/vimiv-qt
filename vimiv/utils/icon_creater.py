# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Create simple versions of QIcon."""

from PyQt5.QtGui import QIcon, QPixmap, QColor

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
    """Return QIcon of size 256 filled with one color.

    Args:
        colorname: Color in hex format, e.g. #000000.
    """
    pixmap = QPixmap(256, 256)
    color = QColor(0, 0, 0)
    color.setNamedColor(colorname)
    pixmap.fill(color)
    return QIcon(pixmap)
