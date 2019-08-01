# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Loghandler to display log messages in the statusbar."""

import logging

from PyQt5.QtCore import pyqtSignal, QObject


class StatusbarLogHandler(QObject, logging.NullHandler):
    """Loghandler to display log messages in the statusbar.

    Only emits a signal on handle which the statusbar connects to.

    Signals:
        message: Emitted with severity and message on log message.
    """

    message = pyqtSignal(str, str)

    def handle(self, record: logging.LogRecord) -> None:
        if record.levelno >= logging.INFO:  # Debug in the statusbar makes no sense
            self.message.emit(record.levelname.lower(), record.message)


handler = StatusbarLogHandler()
