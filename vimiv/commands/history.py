# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to read and write command history."""

import enum
import os
from collections import deque
from typing import Iterable, Optional, Deque, List

from vimiv.commands import argtypes
from vimiv.utils import xdg


def filename() -> str:
    """Return absolute path to history file."""
    return xdg.vimiv_data_dir("history")


def read() -> List[str]:
    """Read command history from file."""
    if not os.path.isfile(filename()):
        return []
    with open(filename()) as f:
        return [line.strip() for line in f]


def write(commands: Iterable[str]):
    """Write command history to file.

    Args:
        commands: Iterable of commands to write.
    """
    with open(filename(), "w") as f:
        for command in commands:
            f.write(command + "\n")


class CycleMode(enum.Enum):
    """Enum defining the different modes for history cycling."""

    Regular = 0
    Substring = 1


class History(deque):
    """Store and interact with command line history.

    Implemented as a deque which stores the commands in the history. Commands with
    different prefixes are not mixed when cycling through history.

    Attributes:
        _prefixes: Valid prefixes for commands to store.
        _tmpdeque: Temporary deque used when cycling through history.
    """

    def __init__(self, prefixes: str, commands: Iterable[str], max_items: int = 100):
        super().__init__(commands, maxlen=max_items)
        self._mode = CycleMode.Regular
        self._prefixes = prefixes
        self._tmpdeque: Optional[Deque[str]] = None

    def update(self, command: str) -> None:
        """Update history with a new command.

        Args:
            command: New command to be inserted.
        """
        if not command or command[0] not in self._prefixes:
            raise ValueError(
                f"Invalid history command, must start with one of {self._prefixes}"
            )
        while command in self:
            self.remove(command)
        self.appendleft(command)

    def reset(self) -> None:
        """Reset history cycling."""
        self._tmpdeque = None

    def cycle(self, direction: argtypes.HistoryDirection, text: str) -> str:
        """Cycle through command history.

        Called from the command line by the history command.

        Args:
            direction: HistoryDirection element.
            text: Current text in the command line.
        Returns:
            The received command to set in the command line.
        """
        return self._cycle_tmpdeque(direction, text, CycleMode.Regular, match=text[0])

    def substr_cycle(self, direction: argtypes.HistoryDirection, text: str) -> str:
        """Cycle through command history with substring matching.

        Called from the command line by the history-substr-search command.

        Args:
            direction: HistoryDirection element.
            text: Current text in the command line used as substring.
        Returns:
            The received command to set in the command line.
        """
        return self._cycle_tmpdeque(direction, text, CycleMode.Substring, match=text)

    def _cycle_tmpdeque(
        self,
        direction: argtypes.HistoryDirection,
        text: str,
        mode: CycleMode,
        match: str,
    ) -> str:
        """Cycle through the temporary deque of matching history elements.

        If there is no temporary deque, a new cycle is started by creating a temporary
        deque with all commands in history starting with match.

        Args:
            direction: HistoryDirection element.
            text: Current text in the command line to prepend to temporary deque.
            match: Text to filter commands by when creating temporary deque.
        Returns:
            The received command to set in the command line.
        """
        if self._tmpdeque is None or mode != self._mode:
            self._mode = mode
            self._tmpdeque = deque(
                cmd for cmd in self if cmd.startswith(match) and cmd != text
            )
            self._tmpdeque.appendleft(text)
        self._tmpdeque.rotate(-1 if direction == direction.Next else 1)
        return self._tmpdeque[0]
