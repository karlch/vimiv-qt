# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Bar widget at the bottom including statusbar and commandline."""

from PyQt5.QtWidgets import QWidget, QStackedLayout, QSizePolicy

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import commandline, statusbar
from vimiv.modes import modehandler
from vimiv.utils import objreg


class Bar(QWidget):
    """Bar at the bottom including statusbar and commandline.

    Attributes:
        statusbar: vimiv.gui.statusbar.StatusBar object.
        commandline: vimiv.gui.commandline.CommandLine object.

        _stack: QStackedLayout containing statusbar and commandline.
    """

    @objreg.register("bar")
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)

        self._stack = QStackedLayout(self)
        self.statusbar = statusbar.StatusBar()
        self._stack.addWidget(self.statusbar)
        self.commandline = commandline.CommandLine()
        self._stack.addWidget(self.commandline)
        self._stack.setCurrentWidget(self.statusbar)

        self.commandline.editingFinished.connect(self.leave_commandline)

    @keybindings.add("colon", "command")
    @commands.argument("text", optional=True, default="")
    @commands.register(instance="bar")
    def command(self, text=""):
        """Enter command mode."""
        self._stack.setCurrentWidget(self.commandline)
        self.commandline.setText(":")
        modehandler.enter("command")

    @keybindings.add("escape", "leave-commandline", mode="command")
    @commands.register(instance="bar", mode="command")
    def leave_commandline(self):
        """Leave command mode."""
        self._stack.setCurrentWidget(self.statusbar)
        self.commandline.setText("")
        modehandler.leave("command")
        self.statusbar.update()
