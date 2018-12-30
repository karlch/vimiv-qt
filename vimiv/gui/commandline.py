# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""CommandLine widget in the bar."""

from PyQt5.QtCore import QCoreApplication, QTimer, pyqtSlot
from PyQt5.QtWidgets import QLineEdit

from vimiv.commands import history, commands, argtypes, runners, search
from vimiv.config import styles, keybindings
from vimiv.modes import modehandler, modewidget, Mode, Modes
from vimiv.utils import objreg, eventhandler


def get_command_func(prefix, command, mode):
    """Return callable function for command depending on prefix."""
    if prefix == ":" and command.startswith("!"):
        return lambda: runners.external(command[1:])
    if prefix == ":":
        return lambda: runners.command(command, mode)
    # No need to search again if incsearch is enabled
    if prefix in "/?" and not search.use_incremental(mode):
        return lambda: search.search(command, mode, reverse=prefix == "?")
    return lambda: None


class UnknownPrefix(Exception):
    """Raised if a prefix in the command line is not known."""

    def __init__(self, prefix):
        """Call the parent with a generated message.

        Args:
            prefix: The unknown prefix.
        """
        message = "Unknown prefix '%s', possible values: %s" % (
            prefix, ", ".join(["'%s'" % (p) for p in CommandLine.PREFIXES]))
        super().__init__(message)


class CommandLine(eventhandler.KeyHandler, QLineEdit):
    """Commandline widget in the bar.

    Class Attributes:
        PREFIXES: Possible prefixes for commands, e.g. ':' or '/'.

    Attributes:
        mode: Mode in which the command is run, corresponds to the mode from
            which the commandline was entered.

        _history: History object to store and interact with history.
    """

    PREFIXES = ":/?"

    STYLESHEET = """
    QLineEdit {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        color: {statusbar.fg};
        border: 0px solid;
        padding: {statusbar.padding};
    }
    """

    @modewidget(Modes.COMMAND)
    @objreg.register
    def __init__(self):
        super().__init__()
        self._history = history.History(history.read())
        self.mode = None

        self.returnPressed.connect(self._on_return_pressed)
        self.editingFinished.connect(self._history.reset)
        self.textEdited.connect(self._on_text_edited)
        self.textChanged.connect(self._incremental_search)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        QCoreApplication.instance().aboutToQuit.connect(self._on_app_quit)
        modehandler.signals.entered.connect(self._on_mode_entered)

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
        command = runners.update_command(command, self.mode)
        # Retrieve function to call depending on prefix
        func = get_command_func(prefix, command, self.mode)
        # Run commands in QTimer so the command line has been left when the
        # command runs
        QTimer.singleShot(0, func)

    def _split_prefix(self, text):
        """Remove prefix from text for command processing.

        Return:
            prefix: One of PREFIXES.
            command: Rest of the text stripped from whitespace.
        """
        prefix, command = text[0], text[1:]
        if prefix not in self.PREFIXES:
            raise UnknownPrefix(prefix)
        command = command.strip()
        return prefix, command

    @pyqtSlot(str)
    def _on_text_edited(self, text):
        if not text:
            self.editingFinished.emit()
        else:
            self._history.reset()

    @pyqtSlot()
    def _incremental_search(self):
        """Run incremental search if enabled."""
        if not search.use_incremental(self.mode):
            return
        try:
            prefix, text = self._split_prefix(self.text())
            if prefix in "/?" and text:
                search.search(text, self.mode, reverse=prefix == "?",
                              incremental=True)
        except IndexError:  # Not enough text
            pass

    @pyqtSlot(int, int)
    def _on_cursor_position_changed(self, _old, new):
        """Prevent the cursor from moving before the prefix."""
        if new < 1:
            self.setCursorPosition(1)

    @keybindings.add("<ctrl>p", "history next", mode=Modes.COMMAND)
    @keybindings.add("<ctrl>n", "history prev", mode=Modes.COMMAND)
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(mode=Modes.COMMAND)
    def history(self, direction):
        """Cycle through command history.

        **syntax:** ``:history direction``

        positional arguments:
            * ``direction``: The direction to cycle in (next/prev).
        """
        self.setText(self._history.cycle(direction, self.text()))

    @keybindings.add("<up>", "history-substr-search next", mode=Modes.COMMAND)
    @keybindings.add("<down>", "history-substr-search prev", mode=Modes.COMMAND)
    @commands.argument("direction", type=argtypes.command_history_direction)
    @commands.register(mode=Modes.COMMAND)
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

    @pyqtSlot(Mode, Mode)
    def _on_mode_entered(self, mode, last_mode):
        """Store mode from which the command line was entered.

        Args:
            mode: The mode entered.
            last_mode: The mode left.
        """
        if mode == Modes.COMMAND:
            self.mode = last_mode


def instance():
    return objreg.get(CommandLine)
