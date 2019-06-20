# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Manipulate widget."""

import logging

from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel

from vimiv import api, utils, imutils
from vimiv.config import styles
from vimiv.imutils import immanipulate
from vimiv.utils import eventhandler, slot


class Manipulate(eventhandler.KeyHandler, QWidget):
    """Manipulate widget displaying progress bars and labels.

    Attributes:
        _error: String containing the current error message.
    """

    STYLESHEET = """
    QWidget {
        font: {statusbar.font};
        color: {manipulate.fg};
        background: {manipulate.bg};
    }

    QProgressBar {
        background: {manipulate.bar.bg};
        border: {manipulate.bar.border};
        text-align: center;
    }

    QProgressBar::chunk {
        background: {manipulate.bar.fg};
    }
    """

    @api.modes.widget(api.modes.MANIPULATE)
    @api.objreg.register
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._error = "No image to manipulate"

        styles.apply(self)

        layout = QHBoxLayout()
        # Add all manipulations from immanipulate
        manipulator = immanipulate.instance()
        for manipulation in manipulator.manipulations:
            layout.addWidget(manipulation.label)
            layout.addWidget(manipulation.bar)
        # Add some spacing
        layout.addStretch()
        layout.addStretch()
        self.setLayout(layout)
        # Connect signals
        imutils.pixmap_loaded.connect(self._on_pixmap_loaded)
        imutils.movie_loaded.connect(self._on_movie_loaded)
        imutils.svg_loaded.connect(self._on_svg_loaded)
        api.modes.MANIPULATE.entered.connect(self._on_entered)
        api.modes.MANIPULATE.left.connect(self.hide)
        # Hide by default
        self.hide()

    @utils.slot
    def _on_entered(self):
        """Show manipulate widget when manipulate mode is entered."""
        if self._error:
            api.modes.MANIPULATE.leave()
            # Must wait for every other statusbar update to complete
            QTimer.singleShot(0, lambda: logging.error(self._error))
        else:
            self.raise_()

    def _on_pixmap_loaded(self, pixmap):
        self._error = None

    def _on_movie_loaded(self, movie):
        self._error = "Manipulating animations is not supported"

    def _on_svg_loaded(self, path):
        self._error = "Manipulating vector graphics is not supported"

    def update_geometry(self, window_width, window_height):
        """Rescale width when main window was resized."""
        y = window_height - self.sizeHint().height()
        self.setGeometry(0, y, window_width, self.sizeHint().height())


class ManipulateImage(QLabel):
    """Overlay image to display the manipulated image in the bottom right.

    It is shown once manipulate mode is entered and hides afterwards.

    Attributes:
        _max_size: TODO
        _pixmap: The manipulated pixmap to display.
    """

    STYLESHEET = """
    QLabel {
        border-top: {manipulate.image.border} {manipulate.image.border.color};
        border-left: {manipulate.image.border} {manipulate.image.border.color};
    }
    """

    def __init__(self, parent, manipulate):
        super().__init__(parent=parent)
        self._max_size = QSize(0, 0)
        self._manipulate = manipulate
        self._pixmap = None
        styles.apply(self)

        api.modes.MANIPULATE.entered.connect(self._on_entered)
        api.modes.MANIPULATE.left.connect(self.hide)
        immanipulate.instance().updated.connect(self._update_pixmap)

        self.hide()

    def update_geometry(self, window_width, window_height):
        """Update position and size according to window size.

        The size is adapted to take up the lower right corner. This is then reduced
        accordingly by displayed pixmap if it is not perfectly square.
        """
        scale = 0.5
        self._max_size = QSize(window_width * scale, window_height * scale)
        if self._pixmap is not None and self.isVisible():
            self._rescale()

    @slot
    def _on_entered(self):
        if self._pixmap is not None:  # No image to display
            self.show()

    @slot
    def _update_pixmap(self, pixmap: QPixmap):
        """Update the displayed pixmap once the manipulated pixmap has changed."""
        self._pixmap = pixmap
        self._rescale()

    def _rescale(self):
        """Rescale pixmap and geometry to fit."""
        # Scale pixmap to fit into label
        pixmap = self._pixmap.scaled(
            self._max_size.width(),
            self._max_size.height(),
            aspectRatioMode=Qt.KeepAspectRatio,
            transformMode=Qt.SmoothTransformation,
        )
        self.setPixmap(pixmap)
        # Update geometry to only show pixmap
        x = self._max_size.width() + (self._max_size.width() - pixmap.width())
        y = (
            self._max_size.height()
            + (self._max_size.height() - pixmap.height())
            - self._manipulate.sizeHint().height()
        )
        self.setGeometry(x, y, pixmap.width(), pixmap.height())


def instance():
    return api.objreg.get(Manipulate)
