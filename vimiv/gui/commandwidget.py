# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Command widget at the bottom including commandline and completion widget."""

from vimiv.qt.core import Qt
from vimiv.qt.widgets import QWidget, QSizePolicy, QVBoxLayout

from vimiv import api
from vimiv.completion import completer
from vimiv.gui import commandline, completionwidget


class CommandWidget(QWidget):
    """Command widget at the bottom including commandline and completion widget.

    Attributes:
        _commandline: Commandline widget to enter text.
        _completer: Completer to handle interaction between command line and completion.
        _completion_widget: Completion widget to display completions.
    """

    @api.objreg.register
    def __init__(self, mainwindow):
        super().__init__(parent=mainwindow)

        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)

        self._commandline = commandline.CommandLine()
        self._completion_widget = completionwidget.CompletionView(mainwindow)
        self._completer = completer.Completer(
            self._commandline, self._completion_widget
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._completion_widget)
        layout.addWidget(self._commandline)
        layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self._commandline.editingFinished.connect(self.leave_commandline)

        self.hide()

    @api.keybindings.register("<colon>", "command", mode=api.modes.MANIPULATE)
    @api.keybindings.register("<colon>", "command")
    @api.commands.register(hide=True, store=False, mode=api.modes.MANIPULATE)
    @api.commands.register(hide=True, store=False)
    def command(self, text: str = ""):
        """Enter command mode.

        **syntax:** ``:command [--text=TEXT]``

        optional arguments:
            * ``--text``: String to append to the ``:`` prefix.
        """
        self._enter_command_mode(":" + text)

    @api.keybindings.register("?", "search --reverse")
    @api.keybindings.register("/", "search")
    @api.commands.register(hide=True, store=False)
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
        api.modes.COMMAND.enter()
        self._commandline.enter(text)
        self._completer.initialize(text)
        self.raise_()
        self.show()
        self.update_geometry(self.parentWidget().width(), self.parentWidget().height())

    @api.keybindings.register("<escape>", "leave-commandline", mode=api.modes.COMMAND)
    @api.commands.register(mode=api.modes.COMMAND)
    def leave_commandline(self):
        """Leave command mode."""
        self._commandline.leave()
        self._completer.reset()
        self.hide()
        api.modes.COMMAND.close()

    def update_geometry(self, window_width, window_height):
        """Update the size and position of the command widgets."""
        self_height = self._commandline.height() + self._completion_widget.height()
        minimum_height = self.parentWidget().height() - window_height
        height = max(self_height, minimum_height)
        self.setGeometry(0, self.parentWidget().height() - height, window_width, height)
