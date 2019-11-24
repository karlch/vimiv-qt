# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Statusbar widget in the bar to display information.

The statusbar is one of the status objects in vimiv. It therefore connects to
the api.status.signals.update signal and updates its content when this signal
was emitted.

Module Attributes:
    statusbar: The statusbar object
"""

from typing import cast

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QLabel, QWidget, QStackedLayout, QHBoxLayout

from vimiv import api, utils
from vimiv.config import styles


statusbar = cast("StatusBar", None)


class StatusBar(QWidget):
    """Statusbar widget to display permanent and temporary messages.

    Packs three labels for permanent messages ("left", "center", "right") and
    one for temporary ones ("message"). The three labels are grouped into one
    hbox. The hbox and the message label are both in a QStackedLayout to toggle
    between them.

    Attributes:
        timer: QTimer object to remove temporary messages after timeout.
        status: Widget grouping the labels for status messages.
        message: Label to display messages.
        stack: Stacked layout to switch between status and message.
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
        self.timer = QTimer()
        self.timer.setInterval(api.settings.statusbar.message_timeout.value)
        self.timer.setSingleShot(True)

        self.status = StatusLabels()
        self.message = QLabel()

        self.stack = QStackedLayout(self)
        self.stack.addWidget(self.status)
        self.stack.addWidget(self.message)
        self.stack.setCurrentWidget(self.status)

        styles.apply(self)

        self.timer.timeout.connect(self.clear_message)
        api.status.signals.clear.connect(self.clear_message)
        utils.log.statusbar_loghandler.message.connect(self._on_message)
        api.status.signals.update.connect(self._on_update_status)
        api.settings.statusbar.message_timeout.changed.connect(self._on_timeout_changed)

    @utils.slot
    def _on_message(self, severity: str, message: str):
        """Display log message when logging was called.

        Args:
            severity: levelname of the log record.
            message: message of the log record.
        """
        self._set_severity_style(severity)
        self.message.setText(message)
        self.stack.setCurrentWidget(self.message)
        self.timer.start()

    @utils.slot
    def _on_update_status(self):
        """Update the statusbar."""
        mode = api.modes.current().name.lower()
        for position, label in self.status:
            text = self._get_text(position, mode)
            label.setText(text)

    @utils.slot
    def clear_message(self):
        """Remove a temporary message from the statusbar."""
        if self.timer.isActive():
            self.timer.stop()
        self._clear_severity_style()
        self.message.clear()
        self.stack.setCurrentWidget(self.status)

    def _on_timeout_changed(self, value: int):
        self.timer.setInterval(value)

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
        return api.status.evaluate(text.replace(" ", "&nbsp;"))

    def _set_severity_style(self, severity):
        """Set the style of the statusbar for a temporary message.

        Adds a colored border to the top of the statusbar. The border color
        depends on the severity.

        Args:
            severity: One of "debug", "info", "warning", "error"
        """
        append = f"""
        QLabel {{
            border-top: {{statusbar.message_border}} {{statusbar.{severity}}};
        }}
        """
        styles.apply(self, append)

    def _clear_severity_style(self):
        styles.apply(self)


class StatusLabels(QWidget):
    """Widget to group the different status labels in the statusbar.

    Attributes:
        left, center, right: The different labels corresponding to their positions.
    """

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self.left = self.label(layout, Qt.AlignLeft)
        self.center = self.label(layout, Qt.AlignCenter)
        self.right = self.label(layout, Qt.AlignRight)

    def __iter__(self):
        yield from zip(
            ("left", "center", "right"), (self.left, self.center, self.right)
        )

    def label(self, layout, alignment):
        """Create a label with this alignment and add it to the layout."""
        label = QLabel()
        label.setAlignment(alignment)
        label.setTextFormat(Qt.RichText)
        layout.addWidget(label)
        return label


def init():
    global statusbar
    statusbar = StatusBar()
