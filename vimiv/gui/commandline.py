# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""CommandLine widget in the bar."""

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QLineEdit

from vimiv.commands import runners, history, commands, argtypes
from vimiv.config import styles, keybindings
from vimiv.modes import modehandler
from vimiv.utils import objreg, eventhandler


class CommandLine(eventhandler.KeyHandler, QLineEdit):
    """Commandline widget in the bar.

    Attributes:
        runners: Dictionary containing the command runners.

        _history: History object to store and interact with history.
    """

    STYLESHEET = """
    QLineEdit {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        color: {statusbar.fg};
        border: 0px solid;
        padding: {statusbar.padding};
    }
    """

    @objreg.register("command")
    def __init__(self):
        super().__init__()
        self.runners = {"command": runners.CommandRunner(),
                        "external": runners.ExternalRunner()}
        self._history = history.History(history.read())

        self.returnPressed.connect(self._on_return_pressed)
        self.editingFinished.connect(self._history.reset)
        self.textEdited.connect(self._on_text_edited)
        QCoreApplication.instance().aboutToQuit.connect(self._write_history)

        compwidget = objreg.get("completion")
        self.textEdited.connect(compwidget.model().filter)
        self.textEdited.connect(compwidget.selectionModel().clear)
        self.editingFinished.connect(compwidget.model().reset)
        compwidget.activated.connect(self._on_completion)

        styles.apply(self)

    def _on_return_pressed(self):
        """Run command and store history on return."""
        prefix, command = self._split_prefix(self.text())
        if not command:  # Only prefix entered
            return
        # Write prefix to history as well for "separate" search history
        self._history.update(prefix + command)
        # Run commands in QTimer so the command line has been left when the
        # command runs
        if prefix == ":" and command.startswith("!"):
            QTimer.singleShot(
                0, lambda: self.runners["external"](command.lstrip(":!")))
        elif prefix == ":":
            # Run the command in the mode from which we entered COMMAND mode
            mode = modehandler.last()
            QTimer.singleShot(
                0, lambda: self.runners["command"](command, mode))
        elif prefix == "/":
            raise NotImplementedError("Search not implemented yet")

    def _split_prefix(self, text):
        """Remove prefix from text for command processing.

        Return:
            prefix: One of ":", "/"
            command: Rest of the text stripped from whitespace.
        """
        prefix, command = text[0], text[1:]
        command = command.strip()
        return prefix, command

    def _on_text_edited(self, text):
        if not text:
            self.editingFinished.emit()
        else:
            self._history.reset()

    @keybindings.add("ctrl+p", "history next", mode="command")
    @keybindings.add("ctrl+n", "history prev", mode="command")
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(instance="command", mode="command")
    def history(self, direction):
        """Cycle through command history.

        Args:
            direction: One of "next", "prev" defining the command to select.
        """
        self.setText(self._history.cycle(direction, self.text()))

    @keybindings.add("up", "history-substr-search next", mode="command")
    @keybindings.add("down", "history-substr-search prev", mode="command")
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(instance="command", mode="command")
    def history_substr_search(self, direction):
        """Cycle through command history with substring matching.

        Args:
            direction: One of "next", "prev" defining the command to select.
        """
        self.setText(self._history.substr_cycle(direction, self.text()))

    def _write_history(self):
        """Write command history to file on quit."""
        history.write(self._history)

    def focusInEvent(self, event):
        """Override focus in event to also prepare completion."""
        super().focusInEvent(event)
        mode = modehandler.last()
        objreg.get("completion").init(mode)

    def focusOutEvent(self, event):
        """Override focus in event to also hide completion."""
        super().focusInEvent(event)
        objreg.get("completion").hide()

    def _on_completion(self, selected_command):
        self.setText(":" + selected_command)
