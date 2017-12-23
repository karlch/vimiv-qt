# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""CommandLine widget in the bar."""

from PyQt5.QtCore import QCoreApplication
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
        QCoreApplication.instance().aboutToQuit.connect(self._write_history)

        styles.apply(self)

    def _on_return_pressed(self):
        """Run command and store history on return."""
        text = self.text()
        self._history.update(text)
        if text.startswith(":!"):
            self.runners["external"](text.lstrip(":!"))
        elif text.startswith(":"):
            # Run the command in the mode from which we entered COMMAND mode
            mode = modehandler.last()
            self.runners["command"](text.lstrip(":"), mode)
        elif text.startswith("/"):
            raise NotImplementedError("Search not implemented yet")

    @keybindings.add("up", "command-history next", mode="command")
    @keybindings.add("down", "command-history prev", mode="command")
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(instance="command", mode="command")
    def command_history(self, direction):
        """Select command from history in command line.

        Args:
            direction: One of "next", "prev" defining the command to select.
        """
        self.setText(self._history.cycle(direction, self.text()))

    def _write_history(self):
        """Write command history to file on quit."""
        history.write(self._history)
