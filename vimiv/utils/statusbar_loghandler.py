# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Loghandler to display log messages in the statusbar."""

import logging

from PyQt5.QtCore import pyqtSignal, QObject


class Signals(QObject):
    """Signals for statusbar log handler.

    Signals:
        message: Emitted with severity and message on log message.
    """

    message = pyqtSignal(str, str)


signals = Signals()


class StatusbarLogHandler(logging.NullHandler):
    """Loghandler to display log messages in the statusbar.

    Only emits a signal on handle which the statusbar connects to.
    """

    def handle(self, record):
        signals.message.emit(record.levelname.lower(), record.message)
