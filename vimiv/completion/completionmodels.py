# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various completion models for command line completion."""

import os
from functools import lru_cache
from typing import List, Set, Tuple

from vimiv import api
from vimiv.commands import aliases
from vimiv.utils import files, trash_manager, escape_ws, unescape_ws


class Empty(api.completion.BaseModel):
    """Empty completion model used as fallback."""

    def __init__(self):
        super().__init__("")


class CommandModel(api.completion.BaseModel):
    """Completion model filled with commands and descriptions."""

    def __init__(self):
        super().__init__(":", column_widths=(0.3, 0.7))

    def on_enter(self, _text: str) -> None:
        """Create command list for appropriate mode when commandline is entered."""
        self.clear()
        mode = api.modes.COMMAND.last
        self.set_data(self.formatted_commands(mode) + self.formatted_aliases(mode))

    @lru_cache(len(api.modes.ALL) - 2)  # ALL without GLOBAL and COMMAND
    def formatted_commands(self, mode: api.modes.Mode) -> List[Tuple[str, str]]:
        """Return list of commands with description for this mode."""
        return [
            (name, command.description)
            for name, command in api.commands.items(mode)
            if not command.hide
        ]

    def formatted_aliases(self, mode: api.modes.Mode) -> List[Tuple[str, str]]:
        """Return list of aliases with explanation for this mode."""
        return [
            (alias, f"Alias for '{command}'")
            for alias, command in aliases.get(mode).items()
        ]


class ExternalCommandModel(api.completion.BaseModel):
    """Completion model filled with shell executables for :!."""

    def __init__(self):
        super().__init__(":!")
        self._initialized = False

    def on_enter(self, _text: str) -> None:
        """Set data when first entering this completion model.

        This allows lazy-loading the external executables on demand.
        """
        if self._initialized:
            return
        executables = self._get_executables()
        self.set_data((f"!{cmd}",) for cmd in executables if not cmd.startswith("."))
        self._initialized = True

    def _get_executables(self) -> List[str]:
        """Return ordered list of shell executables.

        Thanks to aszlig https://github.com/aszlig who wrote the initial
        version of this for the Gtk version of vimiv.
        """
        pathenv = os.environ.get("PATH")
        if pathenv is not None:
            pathdirs = {d for d in pathenv.split(":") if os.path.isdir(d)}
            executables: Set[str] = set()
            for bindir in pathdirs:
                executables |= set(os.listdir(bindir))
            return sorted(executables)
        return []


class StripFilter(api.completion.BaseFilter):
    """Completion filter used for the :command type completions.

    Attributes:
        _command: The command for which this filter is valid.
    """

    def __init__(self, command):
        super().__init__()
        self._command = command

    def filtertext(self, text: str) -> str:
        """Additionally strip command to allow match inside word."""
        return super().filtertext(text.replace(f"{self._command} ", ""))


class PathModel(api.completion.BaseModel):
    """Completion model filled with valid paths for path-like commands.

    Attributes:
        _command: The command for which this model is valid.
        _last_directory: Last directory to avoid re-evaluating on every character.
    """

    def __init__(self, command, valid_modes=api.modes.GLOBALS):
        super().__init__(
            f":{command} ", text_filter=StripFilter(command), valid_modes=valid_modes
        )
        self._command = command
        self._last_directory = ""

    def on_enter(self, text: str) -> None:
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
            self._create_row(os.path.join(directory, os.path.basename(path)))
            for path in images + directories
        ]
        self.set_data(data)

    def _create_row(self, path):
        return (f"{self._command} {escape_ws(path)}",)

    @staticmethod
    def _get_directory(text: str) -> str:
        """Retrieve directory for which the path completion is created."""
        if not text:
            return "."
        if "/" not in text:
            return unescape_ws(text) if os.path.isdir(text) else "."
        return unescape_ws(os.path.dirname(text))


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
            text_filter=StripFilter(f"set {setting.name}"),
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
        for i, suggestion in enumerate(self._setting.suggestions(), start=1):
            values[f"suggestion {i}"] = suggestion
        data = [
            (f"set {self._setting.name} {value}", option)
            for option, value in values.items()
        ]
        self.set_data(data)

    def _on_changed(self, _value):
        """Update data if the value of the setting has changed."""
        self.clear()
        self._update_data()


class TrashModel(api.completion.BaseModel):
    """Completion model filled with valid paths for the :undelete command."""

    def __init__(self):
        super().__init__(
            ":undelete ",
            column_widths=(0.4, 0.45, 0.15),
            valid_modes=api.modes.GLOBALS,
            text_filter=StripFilter("undelete"),
        )

    def on_enter(self, text: str) -> None:
        """Update trash model on enter to include any newly un-/deleted paths."""
        self.clear()
        data = []
        for path in files.listdir(trash_manager.files_directory()):
            cmd = f"undelete {os.path.basename(path)}"
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


class TagModel(api.completion.BaseModel):
    """Completion model filled with valid tag names for the :tag-* commands.

    Attributes:
        _command: Tag command for which the completion model is valid.
    """

    def __init__(self, suffix):
        self._command = f"tag-{suffix}"
        super().__init__(
            f":{self._command} ",
            valid_modes=api.modes.GLOBALS,
            text_filter=StripFilter(self._command),
        )

    def on_enter(self, text: str) -> None:
        """Update tag model on enter to include any new/deleted tags."""
        self.clear()
        data = (
            (f"{self._command} {fname}",) for fname in files.listfiles(api.mark.tagdir)
        )
        self.set_data(data)


class HelpModel(api.completion.BaseModel):
    """Completion model filled with options for :help."""

    def __init__(self):
        super().__init__(
            ":help", column_widths=(0.3, 0.7), text_filter=StripFilter("help")
        )
        self._general = [("help  vimiv", "General information")]
        self._formatted_settings = [
            (f"help {name}", setting.desc) for name, setting in api.settings.items()
        ]

    def on_enter(self, _text: str) -> None:
        """Create help list for appropriate mode when model is entered."""
        self.clear()
        mode = api.modes.COMMAND.last
        self.set_data(
            self._general + self.formatted_commands(mode) + self._formatted_settings
        )

    @lru_cache(len(api.modes.ALL) - 2)  # ALL without GLOBAL and COMMAND
    def formatted_commands(self, mode: api.modes.Mode) -> List[Tuple[str, str]]:
        """Return list of commands with description for this mode."""
        return [
            (f"help :{name}", command.description)
            for name, command in api.commands.items(mode)
        ]


def init():
    """Create completion models."""
    Empty()
    CommandModel()
    ExternalCommandModel()
    PathModel("open")
    PathModel("delete")
    SettingsModel()
    for _, setting in api.settings.items():
        SettingsOptionModel(setting)
    for suffix in ("delete", "load", "write"):
        TagModel(suffix)
    TrashModel()
    HelpModel()
