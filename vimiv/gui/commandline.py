# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""CommandLine widget in the bar."""

from PyQt5.QtWidgets import QLineEdit

from vimiv.commands import runners
from vimiv.config import styles
from vimiv.modes import modehandler
from vimiv.utils import objreg, eventhandler


class CommandLine(eventhandler.KeyHandler, QLineEdit):
    """Commandline widget in the bar.

    Attributes:
        runners: Dictionary containing the command runners.
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
        self.returnPressed.connect(self._on_return_pressed)
        styles.apply(self)

    def _on_return_pressed(self):
        text = self.text()
        if text.startswith(":!"):
            self.runners["external"](text.lstrip(":!"))
        elif text.startswith(":"):
            # Run the command in the mode from which we entered COMMAND mode
            mode = modehandler.last()
            self.runners["command"](text.lstrip(":"), mode)
        elif text.startswith("/"):
            raise NotImplementedError("Search not implemented yet")
