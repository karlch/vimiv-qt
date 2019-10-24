# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Manipulate widget."""

from typing import List, Optional

from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTabWidget

from vimiv import api, utils, imutils
from vimiv.config import styles
from vimiv.imutils import immanipulate
from vimiv.utils import slot, log
from .eventhandler import KeyHandler


class Manipulate(KeyHandler, QTabWidget):
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

    QTabWidget {
        background-color: #00000000;
        border: 0px;
    }
    """

    @api.modes.widget(api.modes.MANIPULATE)
    @api.objreg.register
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._error = "No image to manipulate"

        styles.apply(self)
        # Add all manipulations from immanipulate
        manipulator = immanipulate.Manipulator.instance
        for group in manipulator.manipulations.groups:
            self._add_group(group)
        # Connect signals
        self.currentChanged.connect(manipulator.focus_group_index)
        api.signals.pixmap_loaded.connect(self._on_pixmap_loaded)
        api.signals.movie_loaded.connect(self._on_movie_loaded)
        api.signals.svg_loaded.connect(self._on_svg_loaded)
        api.modes.MANIPULATE.entered.connect(self._on_entered)
        api.modes.MANIPULATE.left.connect(self.hide)
        # Hide by default
        self.hide()

    @api.keybindings.register("<tab>", "next-tab", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def next_tab(self, count: int = 1):
        """Focus the next manipulation tab.

        **count:** multiplier
        """
        self.setCurrentIndex((self.currentIndex() + count) % self.count())

    @api.keybindings.register("<shift><tab>", "prev-tab", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def prev_tab(self, count: int = 1):
        """Focus the previous manipulation tab.

        **count:** multiplier
        """
        self.setCurrentIndex((self.currentIndex() - count) % self.count())

    @staticmethod
    def current() -> str:
        """Current path for manipulate mode."""
        return imutils.current()

    @staticmethod
    def pathlist() -> List[str]:
        """List of current paths for manipulate mode."""
        return imutils.pathlist()

    def _add_group(self, group):
        """Add a group of manipulations into its own tab."""
        widget = QWidget()
        layout = QHBoxLayout()
        for manipulation in group.manipulations:
            layout.addWidget(manipulation.label)
            layout.addWidget(manipulation.slider)
        # Add some spacing for small groups
        for _ in range(4 - len(group.manipulations)):
            layout.addStretch()
        widget.setLayout(layout)
        self.insertTab(-1, widget, group.title)

    @utils.slot
    def _on_entered(self):
        """Show manipulate widget when manipulate mode is entered."""
        if self._error:
            api.modes.MANIPULATE.leave()
            # Must wait for every other statusbar update to complete
            QTimer.singleShot(0, lambda: log.error(self._error))
        else:
            self.raise_()

    def _on_pixmap_loaded(self, _pixmap):
        self._error = None

    def _on_movie_loaded(self, _movie):
        self._error = "Manipulating animations is not supported"

    def _on_svg_loaded(self, _path):
        self._error = "Manipulating vector graphics is not supported"

    def update_geometry(self, window_width, window_height):
        """Rescale width when main window was resized."""
        y = window_height - self.sizeHint().height()
        self.setGeometry(0, y, window_width, self.sizeHint().height())


class ManipulateImage(QLabel):
    """Overlay image to display the manipulated image in the bottom right.

    It is shown once manipulate mode is entered and hides afterwards.

    Attributes:
        _manipulate: The manipulate widget to retrieve y-coordinate.
        _max_size: Maximum size to use up which corresponds to half the window size.
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
        self._manipulate = manipulate
        self._max_size = QSize(0, 0)
        self._pixmap: Optional[QPixmap] = None
        styles.apply(self)

        api.modes.MANIPULATE.entered.connect(self._on_entered)
        api.modes.MANIPULATE.left.connect(self.hide)
        immanipulate.Manipulator.instance.updated.connect(self._update_pixmap)

        self.hide()

    def update_geometry(self, window_width, window_height):
        """Update position and size according to window size.

        The size is adapted to take up the lower right corner. This is then reduced
        accordingly by displayed pixmap if it is not perfectly square.
        """
        self._max_size = QSize(window_width // 2, window_height // 2)
        if self._pixmap is not None and self.isVisible():
            self._rescale()

    @slot
    def _on_entered(self):
        if self._pixmap is not None:  # No image to display
            self.show()
            self.raise_()

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
            - self._manipulate.currentWidget().sizeHint().height()
        )
        self.setGeometry(x, y, pixmap.width(), pixmap.height())
