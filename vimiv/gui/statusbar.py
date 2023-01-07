# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Statusbar widget in the bar to display information.

The statusbar is one of the status objects in vimiv. It therefore connects to
the api.status.signals.update signal and updates its content when this signal
was emitted.

Module Attributes:
    statusbar: The statusbar object
"""

import re

from vimiv.qt.core import Qt
from vimiv.qt.widgets import QLabel, QWidget, QHBoxLayout

from vimiv import api, utils
from vimiv.config import styles


class StatusBar(QWidget):
    """Statusbar widget to display permanent information to the user.

    Packs three labels for permanent information ("left", "center", "right") grouped
    into one hbox.

    Attributes:
        left, center, right: The different labels corresponding to their positions.
    """

    STYLESHEET = """
    QWidget,
    QWidget QLabel {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        color: {statusbar.fg};
        padding-top: {statusbar.padding};
        padding-bottom: {statusbar.padding};
    }
    """

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.left = self.create_label(layout, Qt.AlignLeft)
        self.center = self.create_label(layout, Qt.AlignCenter)
        self.right = self.create_label(layout, Qt.AlignRight)

        styles.apply(self)
        api.status.signals.update.connect(self._update_status)
        api.settings.statusbar.show.changed.connect(self._on_show_changed)

        if not api.settings.statusbar.show.value:
            self.hide()

    def __iter__(self):
        yield from zip(
            ("left", "center", "right"), (self.left, self.center, self.right)
        )

    @classmethod
    def create_label(cls, layout, alignment):
        """Create a label with this alignment and add it to the layout."""
        label = QLabel()
        label.setAlignment(alignment)
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
        return label

    @utils.slot
    def _update_status(self):
        """Update the statusbar."""
        mode = api.modes.current().name.lower()
        for position, label in self:
            text = self._get_text(position, mode)
            label.setText(text)

    def _get_text(self, position, mode):
        """Get the text to put into one label depending on the current mode.

        Args:
            position: One of "left", "center", "right" defining the label.
            mode: Current mode.
        """
        try:  # Prefer mode specific setting
            text = api.settings.get_value(f"statusbar.{position}_{mode}")
        except KeyError:
            text = api.settings.get_value(f"statusbar.{position}")
        return api.status.evaluate(self._escape_subsequent_space_for_html(text))

    @classmethod
    def _escape_subsequent_space_for_html(cls, text):
        return re.sub(r" {2,}", lambda m: m.group().replace(" ", "&nbsp;"), text)

    def _on_show_changed(self, value: bool):
        self.setVisible(value)
