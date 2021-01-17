# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to read and write command history."""

import collections
import enum
import json
import os
from typing import Iterable, Optional, Deque, DefaultDict

from vimiv import api
from vimiv.commands import argtypes
from vimiv.utils import xdg, log


_logger = log.module_logger(__name__)


class CycleMode(enum.Enum):
    """Enum defining the different modes for history cycling."""

    Regular = 0
    Substring = 1


class History(dict):
    """Store and interact with command line history.

    The history dictionary keeps the individual deques of each mode and is able to
    read them from/write them to file.
    """

    def __init__(self, prefixes: str, max_items: int):
        history = self._read(self.filename())
        super().__init__(
            {
                mode: HistoryDeque(prefixes, history[mode.name], max_items=max_items)
                for mode in (*api.modes.GLOBALS, api.modes.MANIPULATE)
            }
        )
        self.migrate_nonmode_based_history()

    def reset(self):
        """Reset history deque of each mode."""
        for history_deque in self.values():
            history_deque.reset()

    def write(self):
        """Write history of each mode to the json file."""
        with open(self.filename(), "w") as f:
            json.dump(
                {mode.name: list(value) for mode, value in self.items()}, f, indent=4
            )

    def migrate_nonmode_based_history(self):
        """Backup and read history from the old text-file history."""
        old_path = self.filename().replace(".json", "")
        if os.path.isfile(old_path):
            with open(old_path, "r") as f:
                old_commands = [line.strip() for line in f]
            backup_name = old_path + ".bak"
            _logger.info(
                "Transferring old non-mode based history file. "
                "A backup is kept at '%s'.",
                backup_name,
            )
            os.rename(old_path, backup_name)
            for history_deque in self.values():
                history_deque.extend(old_commands)

    @classmethod
    def filename(cls):
        """Return absolute path to a history file."""
        return xdg.vimiv_data_dir("history.json")

    @classmethod
    def _read(cls, path: str) -> DefaultDict[str, list]:
        """Read command history from file located at path."""
        history: DefaultDict[str, list] = collections.defaultdict(list)

        try:
            with open(path, "r") as f:
                history.update(json.load(f))
            _logger.debug("Loaded history from '%s'", path)
        except FileNotFoundError:
            _logger.debug("No history file to read")
        except (OSError, json.JSONDecodeError) as e:
            _logger.error("Failed loading history from '%s': %s", path, e)

        return history


class HistoryDeque(collections.deque):
    """Store history of one mode and implement methods for cycling.

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
            self._tmpdeque = collections.deque(
                cmd for cmd in self if cmd.startswith(match) and cmd != text
            )
            self._tmpdeque.appendleft(text)
        self._tmpdeque.rotate(-1 if direction == direction.Next else 1)
        return self._tmpdeque[0]
