# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""CommandLine widget in the bar."""

from PyQt5.QtWidgets import QLineEdit

from vimiv.commands import commands, external
from vimiv.config import styles
from vimiv.utils import objreg, eventhandler


class CommandLine(QLineEdit):
    """Commandline widget in the bar."""

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
        self.returnPressed.connect(self._on_return_pressed)
        styles.apply(self)

    def _on_return_pressed(self):
        text = self.text()
        if text.startswith(":!"):
            external.run(text.lstrip(":!"))
        elif text.startswith(":"):
            commands.run(text.lstrip(":"))
        elif text.startswith("/"):
            raise NotImplementedError("Search not implemented yet")

    @eventhandler.on_key_press("command")
    def keyPressEvent(self, event):
        """Eventhandler parses keys, fallback to default."""
        super().keyPressEvent(event)
