# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Message widget to display temporary information to the user."""

from vimiv.qt.core import Qt, QTimer
from vimiv.qt.widgets import QLabel, QSizePolicy

from vimiv import api, utils
from vimiv.config import styles
from vimiv.gui import statusbar


class Message(QLabel):
    """Message widget to display temporary information to the user.

    Messages are pushed using the logging mechanism. The styling is adopted according to
    the severity of the message. The widget is displayed at the bottom of the window
    using the full window width.

    Attributes:
        _timer: QTimer used to hide the widget upon timeout.
    """

    STYLESHEET = statusbar.StatusBar.STYLESHEET

    def __init__(self, mainwindow):
        super().__init__(parent=mainwindow)

        self._timer = QTimer()
        self._timer.setInterval(api.settings.statusbar.message_timeout.value)
        self._timer.setSingleShot(True)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setWordWrap(True)

        styles.apply(self)
        self.hide()

        self._timer.timeout.connect(self._clear_message)
        api.status.signals.clear.connect(self._clear_message)
        api.settings.statusbar.message_timeout.changed.connect(self._timer.setInterval)
        utils.log.statusbar_loghandler.message.connect(self._on_message)

    def update_geometry(self, window_width, _window_height):
        """Update size according to the window width and the current content."""
        self.setFixedWidth(window_width)  # Ensure full width is used
        self.adjustSize()  # Ensure all text is visible, essentially updates height
        self.move(0, self.parentWidget().height() - self.height())

    @utils.slot
    def _on_message(self, severity: str, message: str):
        """Display log message when logging was called.

        Args:
            severity: levelname of the log record.
            message: message of the log record.
        """
        self._set_severity_style(severity)
        self.setText(message)
        self._timer.start()
        self.raise_()
        self.update_geometry(self.parentWidget().width(), self.parentWidget().height())
        self.show()

    @utils.slot
    def _clear_message(self):
        """Remove a temporary message from the statusbar."""
        if self._timer.isActive():
            self._timer.stop()
        self.clear()
        self.hide()

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
