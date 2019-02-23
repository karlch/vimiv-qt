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
from PyQt5.QtWidgets import QLabel, QWidget, QStackedLayout

from vimiv import api, utils
from vimiv.config import styles
from vimiv.gui import widgets
from vimiv.utils import statusbar_loghandler


statusbar = cast("StatusBar", None)


class StatusBar(QWidget):
    """Statusbar widget to display permanent and temporary messages.

    Packs three labels for permanent messages ("left", "center", "right") and
    one for temporary ones ("message"). The three labels are grouped into one
    hbox. The hbox and the message label are both in a QStackedLayout to toggle
    between them.

    Attributes:
        timer: QTimer object to remove temporary messages after timeout.

        _items: Dictionary storing the widgets.
    """

    STYLESHEET = """
    QWidget,
    QWidget QLabel {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        color: {statusbar.fg};
        padding: {statusbar.padding};
    }
    """

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self._items = {}

        timeout = api.settings.STATUSBAR_MESSAGE_TIMEOUT.value
        self.timer.setInterval(timeout)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.clear_message)
        api.status.signals.clear.connect(self.clear_message)

        self["stack"] = QStackedLayout(self)

        self["status"] = QWidget()
        labelbox = widgets.SimpleHBox(self["status"])
        self["left"] = QLabel()
        self["center"] = QLabel()
        self["center"].setAlignment(Qt.AlignCenter)
        self["right"] = QLabel()
        self["right"].setAlignment(Qt.AlignRight)
        labelbox.addWidget(self["left"])
        labelbox.addWidget(self["center"])
        labelbox.addWidget(self["right"])
        self["stack"].addWidget(self["status"])

        self["message"] = QLabel()
        self["stack"].addWidget(self["message"])
        self["stack"].setCurrentWidget(self["status"])

        styles.apply(self)

        statusbar_loghandler.signals.message.connect(self._on_message)
        api.status.signals.update.connect(self._on_update_status)

    @utils.slot
    def _on_message(self, severity: str, message: str):
        """Display log message when logging was called.

        Args:
            severity: levelname of the log record.
            message: message of the log record.
        """
        self._set_severity_style(severity)
        self["message"].setText(message)
        self["stack"].setCurrentWidget(self["message"])
        self.timer.start()

    @utils.slot
    def _on_update_status(self):
        """Update the statusbar."""
        mode = api.modes.current().name.lower()
        for position in ["left", "center", "right"]:
            label = self[position]
            text = self._get_text(position, mode)
            label.setText(text)

    @utils.slot
    def clear_message(self):
        """Remove a temporary message from the statusbar."""
        if self.timer.isActive():
            self.timer.stop()
        self._clear_severity_style()
        self["message"].setText("")
        self["stack"].setCurrentWidget(self["status"])

    def _get_text(self, position, mode):
        """Get the text to put into one label depending on the current mode.

        Args:
            position: One of "left", "center", "right" defining the label.
            mode: Current mode.
        """
        try:  # Prefer mode specific setting
            text = api.settings.get_value("statusbar.%s_%s" % (position, mode))
        except KeyError:
            text = api.settings.get_value("statusbar.%s" % (position))
        return api.status.evaluate(text)

    def _set_severity_style(self, severity):
        """Set the style of the statusbar for a temporary message.

        Adds a colored border to the top of the statusbar. The border color
        depends on the severity.

        Args:
            severity: One of "debug", "info", "warning", "error"
        """
        append = """
        QLabel {
            border-top: {statusbar.message_border} {statusbar.%s};
        }
        """ % (
            severity
        )
        styles.apply(self, append)

    def _clear_severity_style(self):
        styles.apply(self)

    def __setitem__(self, name, item):
        self._items[name] = item

    def __getitem__(self, name):
        return self._items[name]


def init():
    global statusbar
    statusbar = StatusBar()
