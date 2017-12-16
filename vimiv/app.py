# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Main application class using QApplication."""

from PyQt5.QtWidgets import QApplication

import vimiv
from vimiv.config import keybindings
from vimiv.commands import commands
from vimiv.utils import objreg


class Application(QApplication):
    """Main application class."""

    @objreg.register("app")
    def __init__(self):
        """Initialize the main Qt application."""
        super().__init__([vimiv.__name__])  # Only pass program name to Qt

    @keybindings.add("quit", "q", "global")
    @commands.register(instance="app")
    def quit(self):
        """Quit the QApplication and therefore exit."""
        super().quit()
