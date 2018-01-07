# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Manipulate widget."""

import logging

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QProgressBar, QLabel,
                             QSizePolicy)

from vimiv.config import styles
from vimiv.imutils import imsignals
from vimiv.modes import modehandler
from vimiv.utils import eventhandler, objreg


class Manipulate(eventhandler.KeyHandler, QWidget):
    """Manipulate widget displaying progress bars and labels.

    Attributes:
        _error: String containing the current error message.
        _labels: Dictionary storing the QLabel objects.
        _bar: Dictionary storing the QProgressBar objects.
    """

    STYLESHEET = """
    QWidget {
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

    @objreg.register("manipulate")
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self._error = "No image to manipulate"
        self._labels = {}
        self._bars = {}
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        styles.apply(self)
        self.setFixedHeight(2 * self.height())  # Don't ask me why

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

        imsignals.connect(self._on_pixmap_loaded, "pixmap_loaded")
        imsignals.connect(self._on_movie_loaded, "movie_loaded")
        imsignals.connect(self._on_svg_loaded, "svg_loaded")
        modehandler_obj = objreg.get("mode-handler")
        modehandler_obj.entered.connect(self._on_mode_entered)
        manipulator = objreg.get("manipulator")
        manipulator.edited.connect(self._on_edited)
        manipulator.focused.connect(self._on_focused)
        self.hide()

    def _on_mode_entered(self, mode):
        if mode == "manipulate" and self._error:
            modehandler.leave("manipulate")
            # Must wait for every other statusbar update to complete
            QTimer.singleShot(0, lambda: logging.error(self._error))
        if mode != "manipulate":
            self.hide()

    def _on_edited(self, name, value):
        self._bars[name].setValue(value)

    def _on_focused(self, name):
        fg = styles.get("manipulate.fg")
        fg_focused = styles.get("manipulate.focused.fg")
        for manipulation, label in self._labels.items():
            if manipulation == name:
                label.setText("<span style='color: %s;'>%s</span>"
                              % (fg_focused, manipulation))
            else:
                label.setText("<span style='color: %s;'>%s</span>"
                              % (fg, manipulation))

    def _on_pixmap_loaded(self, pixmap):
        self._error = None

    def _on_movie_loaded(self, movie):
        self._error = "Manipulating animations is not supported"

    def _on_svg_loaded(self, path):
        self._error = "Manipulating vector graphics is not supported"

    def update_geometry(self, window_width, window_height):
        y = window_height - self.height()
        self.setGeometry(0, y, window_width, self.height())
