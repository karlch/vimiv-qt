# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Widget to display partial matches above the statusbar."""

from typing import List, Tuple

from PyQt5.QtCore import pyqtSlot, QTimer, Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy

from vimiv import api, utils
from vimiv.config import styles
from .eventhandler import KeyHandler


class KeyhintWidget(QLabel):
    """Widget to display partial matches above the statusbar.

    The widget is shown when there are partial keybinding matches, e.g. on 'g'. It is
    filled with a list of possible keybindings to fulfill a command.

    Attributes:
        _show_timer: Timer used to show the widget on partial matches after a delay.
        _suffix_color: Color used to display the remaining keys for a match.
        _mainwindow_bottom: y-coordinate of the bottom of the mainwindow.
    """

    STYLESHEET = """
    QLabel {
        font: {statusbar.font};
        color: {statusbar.fg};
        background: {statusbar.bg};
        padding: {keyhint.padding};
        border-top-right-radius: {keyhint.border_radius};
    }
    """

    @api.objreg.register
    def __init__(self, parent):
        super().__init__(parent=parent)
        self._show_timer = QTimer(self)
        self._show_timer.setSingleShot(True)
        self._show_timer.setInterval(api.settings.keyhint.delay.value)
        self._show_timer.timeout.connect(self.show)

        self._suffix_color = styles.get("keyhint.suffix_color")
        self._mainwindow_bottom = 0

        styles.apply(self)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setTextFormat(Qt.RichText)

        KeyHandler.partial_handler.partial_matches.connect(self._on_partial_matches)
        KeyHandler.partial_handler.partial_cleared.connect(self._on_partial_cleared)
        api.settings.keyhint.delay.changed.connect(self._on_delay_changed)

        self.hide()

    def update_geometry(self, _window_width, window_bottom):
        """Adapt location when main window geometry changes."""
        self._mainwindow_bottom = window_bottom
        self._update_geometry()

    def _update_geometry(self):
        """Update geometry according to current text content and window location."""
        self.adjustSize()
        y = self._mainwindow_bottom - self.height()
        self.setGeometry(0, y, self.width(), self.height())

    @pyqtSlot(str, list)
    def _on_partial_matches(self, prefix: str, matches: List[Tuple[str, str]]):
        """Initialize widget when partial matches exist.

        Args:
            prefix: Key(s) pressed for which there are partial matches.
            matches: List of keybindings and commands that can complete the partial.
        """
        self._show_timer.start()
        text = ""
        for keybinding, command in matches:
            suffix = keybinding[len(prefix) :]
            text += (
                "<tr>"
                f"<td>{prefix}</td>"
                f"<td style='color: {self._suffix_color}'>{suffix}</td>"
                f"<td style='padding-left: 2ex'>{command}</td>"
                "</tr>"
            )
        self.setText(f"<table>{text}</table>")
        self._update_geometry()

    @utils.slot
    def _on_partial_cleared(self):
        """Stop timer and hide widget when there are no partial matches to show."""
        self._show_timer.stop()
        self.hide()

    def _on_delay_changed(self, value: int):
        """Update timer interval if the keyhint delay setting changed."""
        self._show_timer.setInterval(value)

    def show(self):
        """Override show to always raise the widget in addition."""
        super().show()
        self.raise_()
