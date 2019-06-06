# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Manipulate widget."""

import logging

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QProgressBar, QLabel

from vimiv import api, utils, imutils
from vimiv.config import styles
from vimiv.imutils import immanipulate
from vimiv.utils import eventhandler, wrap_style_span


class Manipulate(eventhandler.KeyHandler, QWidget):
    """Manipulate widget displaying progress bars and labels.

    Attributes:
        _error: String containing the current error message.
        _labels: Dictionary storing the QLabel objects.
        _bar: Dictionary storing the QProgressBar objects.
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
        self._labels = {}
        self._bars = {}

        styles.apply(self)

        layout = QHBoxLayout()

        for manipulation in ["brightness", "contrast"]:
            bar = QProgressBar()
            bar.setValue(0)
            bar.setMinimum(-127)
            bar.setMaximum(127)
            bar.setFormat("%v")
            label = QLabel(manipulation)
            layout.addWidget(label)
            layout.addWidget(bar)
            self._bars[manipulation] = bar
            self._labels[manipulation] = label
        self._on_focused("brightness")  # Default selection

        layout.addStretch()
        layout.addStretch()
        self.setLayout(layout)

        imutils.pixmap_loaded.connect(self._on_pixmap_loaded)
        imutils.movie_loaded.connect(self._on_movie_loaded)
        imutils.svg_loaded.connect(self._on_svg_loaded)
        api.modes.MANIPULATE.entered.connect(self._on_entered)
        api.modes.MANIPULATE.left.connect(self.hide)
        manipulator = immanipulate.instance()
        manipulator.edited.connect(self._on_edited)
        manipulator.focused.connect(self._on_focused)

        self.hide()

    @api.keybindings.register("<escape>", "discard", mode=api.modes.MANIPULATE)
    @api.commands.register(mode=api.modes.MANIPULATE)
    def discard(self):
        """Discard any changes and leave manipulate."""
        api.modes.MANIPULATE.leave()
        self._reset()
        immanipulate.instance().reset()

    @utils.slot
    def _on_entered(self):
        """Show manipulate widget when manipulate mode is entered."""
        if self._error:
            api.modes.MANIPULATE.leave()
            # Must wait for every other statusbar update to complete
            QTimer.singleShot(0, lambda: logging.error(self._error))
        else:
            self.raise_()

    def _on_edited(self, name, value):
        """Update progressbar value on edit."""
        self._bars[name].setValue(value)

    def _on_focused(self, name):
        """Highlight newly focused mode label.

        Args:
            name: Name of the label focused.
        """
        fg = styles.get("manipulate.fg")
        fg_focused = styles.get("manipulate.focused.fg")
        for manipulation, label in self._labels.items():
            if manipulation == name:
                label.setText(wrap_style_span(f"color: {fg_focused}", manipulation))
            else:
                label.setText(wrap_style_span(f"color: {fg}", manipulation))

    def _on_pixmap_loaded(self, pixmap):
        self._error = None

    def _on_movie_loaded(self, movie):
        self._error = "Manipulating animations is not supported"

    def _on_svg_loaded(self, path):
        self._error = "Manipulating vector graphics is not supported"

    def update_geometry(self, window_width, window_height):
        """Rescale width when main window was resized."""
        y = window_height - self.height()
        self.setGeometry(0, y, window_width, self.height())

    def height(self):
        """Update height to get preferred height of the progress bar."""
        return self._bars["brightness"].sizeHint().height() * 2

    def _reset(self):
        """Reset values of all widgets to default."""
        for bar in self._bars.values():
            bar.setValue(0)


def instance():
    return api.objreg.get(Manipulate)
