# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""CommandLine widget in the bar."""

import contextlib
from typing import cast, TYPE_CHECKING

from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtWidgets import QLineEdit

from vimiv import api, utils
from vimiv.commands import argtypes, runners, search
from vimiv.config import styles
from vimiv.gui import eventhandler

if TYPE_CHECKING:
    from vimiv.commands import history


class CommandLine(eventhandler.EventHandlerMixin, QLineEdit):
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
        padding-top: {statusbar.padding};
        padding-bottom: {statusbar.padding};
    }
    """

    @api.modes.widget(api.modes.COMMAND)
    @api.objreg.register
    def __init__(self) -> None:
        super().__init__()

        self.mode: api.modes.Mode = api.modes.IMAGE
        self._history = cast("history.History", None)

        api.modes.COMMAND.first_entered.connect(self.init)

    def init(self) -> None:
        """Lazy-initialize command-line when first entering command mode."""
        from vimiv.commands import history

        self._history = history.History(
            self.PREFIXES, max_items=api.settings.command.history_limit.value,
        )

        self.returnPressed.connect(self._on_return_pressed)
        self.textEdited.connect(self._on_text_edited)
        self.textChanged.connect(self._incremental_search)
        self.cursorPositionChanged.connect(self._on_cursor_position_changed)
        QCoreApplication.instance().aboutToQuit.connect(  # type: ignore
            self._history.write
        )

        styles.apply(self)

    def pathlist(self):
        return api.modes.COMMAND.last.widget.pathlist()

    def current(self):
        return api.modes.COMMAND.last.widget.current()

    def enter(self, text: str):
        self.setText(text)
        self.mode = api.modes.COMMAND.last

    def leave(self):
        self.clear()
        self._history.reset()

    @utils.slot
    def _on_return_pressed(self) -> None:
        """Run command and store history on return."""
        prefix, command = self._split_prefix(self.text())
        if not command:  # Only prefix entered
            return
        self._history[self.mode].update(prefix + command)
        # Run commands in QTimer so the command line has been left when the
        # command runs
        if prefix == ":":
            QTimer.singleShot(0, lambda: runners.run(command, mode=self.mode))
        elif not search.use_incremental(self.mode):
            QTimer.singleShot(
                0, lambda: search.search(command, self.mode, reverse=prefix == "?")
            )

    def _split_prefix(self, text):
        """Remove prefix from text for command processing.

        Returns:
            prefix: One of PREFIXES.
            command: Rest of the text stripped from whitespace.
        """
        prefix, command = text[0], text[1:]
        if prefix not in self.PREFIXES:
            possible = utils.quotedjoin(self.PREFIXES)
            raise ValueError(f"Unknown prefix '{prefix}', possible values: {possible}")
        command = command.strip()
        return prefix, command

    @utils.slot
    def _on_text_edited(self, text: str) -> None:
        if not text:
            self.editingFinished.emit()
        else:
            self._history.reset()

    @utils.slot
    def _incremental_search(self) -> None:
        """Run incremental search if enabled."""
        if not search.use_incremental(self.mode):
            return
        with contextlib.suppress(IndexError):  # Not enough text
            prefix, text = self._split_prefix(self.text())
            if prefix in "/?" and text:
                search.search(text, self.mode, reverse=prefix == "?", incremental=True)

    @utils.slot
    def _on_cursor_position_changed(self, _old: int, new: int):
        """Prevent the cursor from moving before the prefix."""
        if new < 1:
            self.setCursorPosition(1)

    @api.keybindings.register("<ctrl>p", "history next", mode=api.modes.COMMAND)
    @api.keybindings.register("<ctrl>n", "history prev", mode=api.modes.COMMAND)
    @api.commands.register(mode=api.modes.COMMAND)
    def history(self, direction: argtypes.HistoryDirection):
        """Cycle through command history.

        **syntax:** ``:history direction``

        positional arguments:
            * ``direction``: The direction to cycle in (next/prev).
        """
        self.setText(self._history[self.mode].cycle(direction, self.text()))

    @api.keybindings.register(
        "<up>", "history-substr-search next", mode=api.modes.COMMAND
    )
    @api.keybindings.register(
        "<down>", "history-substr-search prev", mode=api.modes.COMMAND
    )
    @api.commands.register(mode=api.modes.COMMAND)
    def history_substr_search(self, direction: argtypes.HistoryDirection):
        """Cycle through command history with substring matching.

        **syntax:** ``:history-substr-search direction``

        positional arguments:
            * ``direction``: The direction to cycle in (next/prev).
        """
        self.setText(self._history[self.mode].substr_cycle(direction, self.text()))

    @api.commands.register(mode=api.modes.MANIPULATE)
    @api.commands.register()
    def history_clear(self, mode: bool = False):
        """Clear the command history.

        This clears the history of all modes unless ``--mode`` is passed.

        **syntax:** ``:history-clear [--mode]``

        optional arguments:
            * ``--mode``: Clear the history of the current mode only.
        """
        if mode:
            self._history[self.mode].clear()
        else:
            for historydeque in self._history.values():
                historydeque.clear()

    def focusOutEvent(self, event):
        """Override focus out event to not emit editingFinished."""
