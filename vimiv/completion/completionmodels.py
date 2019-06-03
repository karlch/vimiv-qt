# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various completion models for command line completion."""

import os
import shlex
from typing import List, Set

from vimiv import api
from vimiv.commands import aliases
from vimiv.utils import files, trash_manager


class Empty(api.completion.BaseModel):
    """Empty completion model used as fallback."""

    def __init__(self):  # type: ignore
        super().__init__("")


class CommandModel(api.completion.BaseModel):
    """Completion model filled with commands and descriptions."""

    def __init__(self):
        super().__init__(":", column_widths=(0.3, 0.7))

    def on_enter(self, _text: str, mode: api.modes.Mode) -> None:
        """Create command list for appropriate mode when commandline is entered."""
        self.clear()
        cmdlist = []
        # Include commands
        for name, command in api.commands.items(mode):
            if not command.hide:
                cmdlist.append((name, command.description))
        # Include aliases
        for alias, cmd in aliases.get(mode).items():
            desc = "Alias for '%s'." % (cmd)
            cmdlist.append((alias, desc))
        self.set_data(cmdlist)


class ExternalCommandModel(api.completion.BaseModel):
    """Completion model filled with shell executables for :!."""

    def __init__(self):
        super().__init__(":!")
        executables = self._get_executables()
        data = [["!%s" % (cmd)] for cmd in executables if not cmd.startswith(".")]
        self.set_data(data)

    def _get_executables(self) -> List[str]:
        """Return ordered list of shell executables.

        Thanks to aszlig https://github.com/aszlig who wrote the initial
        version of this for the Gtk version of vimiv.
        """
        pathenv = os.environ.get("PATH")
        if pathenv is not None:
            pathdirs = [d for d in pathenv.split(":") if os.path.isdir(d)]
            executables: Set[str] = set()
            for bindir in pathdirs:
                executables |= set(os.listdir(bindir))
            return sorted(executables)
        return []


class StripFilter(api.completion.TextFilter):
    """TextFilter used for the :command type completions.

    Attributes:
        _command: The command for which this filter is valid.
    """

    def __init__(self, command):
        super().__init__()
        self._command = command

    def strip_text(self, text: str) -> str:
        """Additionally strip :command to allow match inside word."""
        return (
            super()
            .strip_text(text)
            .replace(f"{self._command} ", "")  # Still allow match inside word for open
        )


class PathModel(api.completion.BaseModel):
    """Completion model filled with valid paths for the :open command.

    Attributes:
        _last_directory: Last directory to avoid re-evaluating on every character.
    """

    def __init__(self):
        super().__init__(":open ", text_filter=StripFilter("open"))
        self._last_directory = ""

    def on_enter(self, text: str, mode: api.modes.Mode) -> None:
        """Update completion options on enter."""
        self.on_text_changed(text)

    def on_text_changed(self, text: str) -> None:
        """Update completion options when text changes."""
        directory = self._get_directory(text)
        # Nothing changed
        if os.path.abspath(directory) == self._last_directory:
            return
        # Prepare
        self._last_directory = os.path.abspath(directory)
        self.clear()
        # No completinos for non-existent directory
        if not os.path.isdir(os.path.expanduser(directory)):
            return
        # Retrieve supported paths
        images, directories = files.supported(files.listdir(directory))
        # Format data
        data = [
            ("open " + shlex.quote(os.path.join(directory, os.path.basename(path))),)
            for path in images + directories
        ]
        self.set_data(data)

    @staticmethod
    def _get_directory(text: str) -> str:
        """Retrieve directory for which the path completion is created."""
        if not text:
            return "."
        if "/" not in text:
            return text if os.path.isdir(text) else "."
        return os.path.dirname(text)


class SettingsModel(api.completion.BaseModel):
    """Completion model filled with valid options for the :set command."""

    def __init__(self):
        super().__init__(
            ":set ", text_filter=StripFilter("set"), column_widths=(0.4, 0.1, 0.5)
        )
        data = [
            (f"set {name}", str(setting), setting.desc)
            for name, setting in api.settings.items()
            if not setting.hidden
        ]
        self.set_data(data)


class SettingsOptionModel(api.completion.BaseModel):
    """Completion model filled with suggestions for a specific setting.

    Attributes:
        _setting: The corresponding settings object.
    """

    def __init__(self, setting: api.settings.Setting):
        super().__init__(
            f":set {setting.name}",
            text_filter=StripFilter("set"),
            column_widths=(0.5, 0.5),
        )
        self._setting = setting
        self.setSortRole(3)
        setting.changed.connect(self._on_changed)
        self._update_data()

    def _update_data(self):
        """Update model content with current setting value."""
        values = {
            "default": str(self._setting.default),
            "current": str(self._setting.value),
        }
        for i, suggestion in enumerate(self._setting.suggestions()):
            values["suggestion %d" % (i + 1)] = suggestion
        data = [
            (f"set {self._setting.name} {value}", option)
            for option, value in values.items()
        ]
        self.set_data(data)

    def _on_changed(self, _value):
        """Update data if the value of the setting has changed."""
        self._update_data()


class TrashModel(api.completion.BaseModel):
    """Completion model filled with valid paths for the :undelete command.

    Attributes:
        _initialized: Bool to allow only re-creating the completion options on_enter.
    """

    def __init__(self):
        super().__init__(":undelete ", column_widths=(0.4, 0.45, 0.15))
        self._initialized = False

    def on_enter(self, text: str, mode: api.modes.Mode) -> None:
        """Update trash model on enter."""
        self._initialized = False
        self.on_text_changed(text)

    def on_text_changed(self, text: str) -> None:
        """Update trash model the once when text changed.

        This is required in addition to on_enter as it is very likely to enter trash
        completion by typing :undelete.
        """
        if self._initialized:
            return
        self.clear()
        data = []
        for path in files.listdir(trash_manager.files_directory()):
            cmd = "undelete %s" % (os.path.basename(path))
            # Get info and format it neatly
            original, date = trash_manager.trash_info(path)
            original = original.replace(os.path.expanduser("~"), "~")
            original = os.path.dirname(original)
            date = "%s-%s-%s %s:%s" % (
                date[2:4],
                date[4:6],
                date[6:8],
                date[9:11],
                date[11:13],
            )
            # Append data in column form
            data.append((cmd, original, date))
        self.set_data(data)
        self._initialized = True


def init():
    """Create completion models."""
    Empty()
    CommandModel()
    ExternalCommandModel()
    PathModel()
    SettingsModel()
    for _, setting in api.settings.items():
        SettingsOptionModel(setting)
    TrashModel()
