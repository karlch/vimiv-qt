# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Bar widget at the bottom including statusbar and commandline."""

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWidget, QStackedLayout, QSizePolicy

from vimiv import api
from vimiv.gui import commandline, statusbar


class Bar(QWidget):
    """Bar at the bottom including statusbar and commandline.

    Attributes:
        commandline: vimiv.gui.commandline.CommandLine object.

        _stack: QStackedLayout containing statusbar and commandline.
    """

    @api.objreg.register
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        statusbar.init()
        self.commandline = commandline.CommandLine()
        self._stack = QStackedLayout(self)

        self._stack.addWidget(statusbar.statusbar)
        self._stack.addWidget(self.commandline)
        self._stack.setCurrentWidget(statusbar.statusbar)

        self._maybe_hide()

        self.commandline.editingFinished.connect(self._on_editing_finished)
        api.settings.signals.changed.connect(self._on_settings_changed)

    @api.keybindings.register("<colon>", "command", mode=api.modes.MANIPULATE)
    @api.keybindings.register("<colon>", "command")
    @api.commands.register(hide=True, mode=api.modes.MANIPULATE)
    @api.commands.register(hide=True)
    def command(self, text: str = ""):
        """Enter command mode.

        **syntax:** ``:command [--text=TEXT]``

        optional arguments:
            * ``text``: String to append to the ``:`` prefix.
        """
        self._enter_command_mode(":" + text)

    @api.keybindings.register("?", "search --reverse")
    @api.keybindings.register("/", "search")
    @api.commands.register(hide=True)
    def search(self, reverse: bool = False):
        """Start a search.

        **syntax:** ``:search [--reverse]``

        optional arguments:
            * ``--reverse``: Search in reverse direction.
        """
        if reverse:
            self._enter_command_mode("?")
        else:
            self._enter_command_mode("/")

    def _enter_command_mode(self, text):
        """Enter command mode setting the text to text."""
        self.show()
        self._stack.setCurrentWidget(self.commandline)
        self.commandline.setText(text)
        api.modes.enter(api.modes.COMMAND)

    @api.keybindings.register("<escape>", "leave-commandline",
                         mode=api.modes.COMMAND)
    @api.commands.register(mode=api.modes.COMMAND)
    def leave_commandline(self):
        """Leave command mode."""
        self.commandline.editingFinished.emit()

    @pyqtSlot()
    def _on_editing_finished(self):
        """Leave command mode on the editingFinished signal."""
        self.commandline.setText("")
        self._stack.setCurrentWidget(statusbar.statusbar)
        self._maybe_hide()
        api.modes.leave(api.modes.COMMAND)

    @pyqtSlot(api.settings.Setting)
    def _on_settings_changed(self, setting):
        """React to changed settings."""
        if setting == api.settings.STATUSBAR_SHOW:
            statusbar.statusbar.setVisible(setting.value)
            self._maybe_hide()
        elif setting == api.settings.STATUSBAR_MESSAGE_TIMEOUT:
            statusbar.statusbar.timer.setInterval(setting.value)

    def _maybe_hide(self):
        """Hide bar if statusbar is not visible and not in command mode."""
        always_show = api.settings.STATUSBAR_SHOW.value
        if not always_show and not self.commandline.hasFocus():
            self.hide()
        else:
            self.show()


def instance():
    return api.objreg.get(Bar)
