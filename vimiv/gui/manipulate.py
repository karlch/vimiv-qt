# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Manipulate widget."""

from typing import List, Optional

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QTabWidget

from vimiv import api, utils, imutils
from vimiv.config import styles
from vimiv.imutils import immanipulate
from vimiv.utils import slot
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

        styles.apply(self)
        # Add all manipulations from immanipulate
        manipulator = immanipulate.Manipulator.instance
        for group in manipulator.manipulations.groups:
            self._add_group(group)
        # Connect signals
        self.currentChanged.connect(manipulator.focus_group_index)
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

        api.modes.MANIPULATE.left.connect(self._on_left)
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
    def _update_pixmap(self, pixmap: QPixmap):
        """Update the manipulate pixmap and show manipulate widgets if needed."""
        if not self.isVisible():
            self._manipulate.raise_()
            self.raise_()
            self.show()
        self._pixmap = pixmap
        self._rescale()

    @utils.slot
    def _on_left(self):
        """Hide manipulate widgets when leaving manipulate mode."""
        self.hide()
        self._manipulate.hide()

    def _rescale(self):
        """Rescale pixmap and geometry to fit."""
        assert self._pixmap is not None, "No pixmap to rescale"
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
