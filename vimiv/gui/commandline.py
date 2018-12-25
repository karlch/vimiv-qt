# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""CommandLine widget in the bar."""

from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSlot
from PyQt5.QtWidgets import QLineEdit

from vimiv.commands import history, commands, argtypes, runners, search
from vimiv.config import styles, keybindings, settings
from vimiv.modes import modehandler
from vimiv.utils import objreg, eventhandler


class CommandLine(eventhandler.KeyHandler, QLineEdit):
    """Commandline widget in the bar.

    Attributes:
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
        self._history = history.History(history.read())

        self.returnPressed.connect(self._on_return_pressed)
        self.editingFinished.connect(self._history.reset)
        self.textEdited.connect(self._on_text_edited)
        self.textChanged.connect(self._incremental_search)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        QCoreApplication.instance().aboutToQuit.connect(self._on_app_quit)

        styles.apply(self)

    @pyqtSlot()
    def _on_return_pressed(self):
        """Run command and store history on return."""
        prefix, command = self._split_prefix(self.text())
        if not command:  # Only prefix entered
            return
        # Write prefix to history as well for "separate" search history
        self._history.update(prefix + command)
        # Update command with aliases and wildcards
        mode = modehandler.last()
        command = runners.alias(command, mode)
        command = runners.expand_wildcards(command, mode)
        # Retrieve function to call depending on prefix
        func = self._get_command_func(prefix, command, mode)
        # Run commands in QTimer so the command line has been left when the
        # command runs
        QTimer.singleShot(0, func)

    def _split_prefix(self, text):
        """Remove prefix from text for command processing.

        Return:
            prefix: One of ":", "/"
            command: Rest of the text stripped from whitespace.
        """
        prefix, command = text[0], text[1:]
        command = command.strip()
        return prefix, command

    def _get_command_func(self, prefix, command, mode):
        """Return callable function for command depending on prefix."""
        if prefix == ":" and command.startswith("!"):
            return lambda: runners.external(command[1:])
        if prefix == ":":
            return lambda: runners.command(command)
        # No need to search again if incsearch is enabled
        if prefix in "/?" and not self._use_incremental_search():
            return lambda: search.search(command, mode, reverse=prefix == "?")
        return lambda: None

    @pyqtSlot(str)
    def _on_text_edited(self, text):
        if not text:
            self.editingFinished.emit()
        else:
            self._history.reset()

    @pyqtSlot()
    def _incremental_search(self):
        """Run incremental search if enabled."""
        if not self._use_incremental_search():
            return
        try:
            prefix, text = self._split_prefix(self.text())
            if prefix in "/?" and text:
                search.search(text, modehandler.last(), reverse=prefix == "?",
                              incremental=True)
        except IndexError:  # Not enough text
            pass

    def _use_incremental_search(self):
        """Return True if incremental search should be used."""
        enabled = settings.get_value(settings.Names.SEARCH_INCREMENTAL)
        if enabled and modehandler.last() in ["library", "thumbnail"]:
            return True
        return False

    @pyqtSlot(int, int)
    def _on_cursor_position_changed(self, _old, new):
        """Prevent the cursor from moving before the prefix."""
        if new < 1:
            self.setCursorPosition(1)

    @keybindings.add("<ctrl>p", "history next", mode="command")
    @keybindings.add("<ctrl>n", "history prev", mode="command")
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(instance="command", mode="command")
    def history(self, direction):
        """Cycle through command history.

        **syntax:** ``:history direction``

        positional arguments:
            * ``direction``: The direction to cycle in (next/prev).
        """
        self.setText(self._history.cycle(direction, self.text()))

    @keybindings.add("<up>", "history-substr-search next", mode="command")
    @keybindings.add("<down>", "history-substr-search prev", mode="command")
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(instance="command", mode="command")
    def history_substr_search(self, direction):
        """Cycle through command history with substring matching.

        **syntax:** ``:history-substr-search direction``

        positional arguments:
            * ``direction``: The direction to cycle in (next/prev).
        """
        self.setText(self._history.substr_cycle(direction, self.text()))

    @pyqtSlot()
    def _on_app_quit(self):
        """Write command history to file on quit."""
        history.write(self._history)

    def focusOutEvent(self, event):
        """Override focus out event to not emit editingFinished."""
