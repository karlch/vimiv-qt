# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Manipulate widget."""

from typing import List, Optional

from vimiv.qt.core import Qt, QSize, QPoint
from vimiv.qt.gui import QPixmap
from vimiv.qt.widgets import QWidget, QHBoxLayout, QLabel, QTabWidget

from vimiv import api, utils, imutils, qt
from vimiv.config import styles
from vimiv.imutils import immanipulate
from vimiv.gui import eventhandler
from vimiv.utils import slot


class Manipulate(eventhandler.EventHandlerMixin, QTabWidget):
    """Manipulate widget displaying progress bars and labels.

    Attributes:
        _image: ManipulateImage displayed at the top right of the manipulate widget.
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
    def __init__(self, mainwindow):
        super().__init__(parent=mainwindow)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        styles.apply(self)
        # Add all manipulations from immanipulate
        manipulator = immanipulate.Manipulator.instance
        for group in manipulator.manipulations.groups:
            self._add_group(group)

        self._image = ManipulateImage(mainwindow, manipulator)
        # Connect signals
        self.currentChanged.connect(manipulator.focus_group_index)
        api.modes.MANIPULATE.closed.connect(self._close)

    @property
    def _mainwindow(self):
        return self.parentWidget()

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
        if self.isVisible():
            y = window_height - self.sizeHint().height()
            self.setGeometry(0, y, window_width, self.sizeHint().height())
            size_image = QSize(window_width // 2, window_height // 2)
            y_image = window_height - self.currentWidget().height()
            self._image.update_geometry(size_image, QPoint(window_width, y_image))

    def show(self):
        """Override show to also raise and show the image."""
        super().show()
        self._image.show()
        self.update_geometry(self._mainwindow.width(), self._mainwindow.bottom)
        self.raise_()
        self._image.raise_()

    @utils.slot
    def _close(self):
        """Hide manipulate widgets when closing manipulate mode."""
        self.hide()
        self._image.hide()


class ManipulateImage(QLabel):
    """Overlay image to display the manipulated image in the bottom right.

    It is shown once manipulate mode is entered and hides afterwards.

    Attributes:
        _bottom_right: Point describing the expected bottom right of this widget.
        _max_size: Maximum size to use up which corresponds to half the window size.
        _pixmap: The manipulated pixmap to display.
    """

    STYLESHEET = """
    QLabel {
        border-top: {manipulate.image.border} {manipulate.image.border.color};
        border-left: {manipulate.image.border} {manipulate.image.border.color};
    }
    """

    def __init__(self, parent, manipulator: immanipulate.Manipulator):
        super().__init__(parent=parent)
        self._max_size = QSize(0, 0)
        self._pixmap: Optional[QPixmap] = None
        self._bottom_right = QPoint(0, 0)
        styles.apply(self)

        manipulator.updated.connect(self._update_pixmap)

    def update_geometry(self, size: QSize, bottom_right: QPoint):
        """Update position and size according to size and bottom_right.

        The size is adapted to take up the lower right corner. This is then reduced
        accordingly by displayed pixmap if it is not perfectly square.
        """
        self._max_size = size
        self._bottom_right = bottom_right
        if self._pixmap is not None:
            self._rescale()

    @slot
    def _update_pixmap(self, pixmap: QPixmap):
        """Update the manipulate pixmap and show manipulate widgets if needed."""
        self._pixmap = pixmap
        self._rescale()

    def _rescale(self):
        """Rescale pixmap and geometry to fit."""
        assert self._pixmap is not None, "No pixmap to rescale"
        # Scale pixmap to fit into label
        # Workaround for different keyword naming in PySide6
        if qt.USE_PYSIDE6:
            pixmap = self._pixmap.scaled(
                self._max_size.width(),
                self._max_size.height(),
                aspectMode=Qt.AspectRatioMode.KeepAspectRatio,
                mode=Qt.TransformationMode.SmoothTransformation,
            )
        else:
            pixmap = self._pixmap.scaled(
                self._max_size.width(),
                self._max_size.height(),
                aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
                transformMode=Qt.TransformationMode.SmoothTransformation,
            )
        self.setPixmap(pixmap)
        # Update geometry to only show pixmap
        x = self._bottom_right.x() - pixmap.width()
        y = self._bottom_right.y() - pixmap.height()
        self.setGeometry(x, y, pixmap.width(), pixmap.height())
