# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Various completion models for command line completion."""

import functools
import os
import re
from typing import List, Set, Tuple

from vimiv import api
from vimiv.commands import aliases
from vimiv.utils import files, trash_manager


class CommandModel(api.completion.BaseModel):
    """Completion model filled with commands and descriptions."""

    def __init__(self):
        super().__init__(":", column_widths=(0.3, 0.7))

    def on_enter(self, _text: str) -> None:
        """Create command list for appropriate mode when commandline is entered."""
        mode = api.modes.COMMAND.last
        self.set_data(self.formatted_commands(mode) + self.formatted_aliases(mode))

    @functools.lru_cache(len(api.modes.ALL) - 2)  # ALL without GLOBAL and COMMAND
    def formatted_commands(self, mode: api.modes.Mode) -> List[Tuple[str, str]]:
        """Return list of commands with description for this mode."""
        return [
            (f":{name}", command.description)
            for name, command in api.commands.items(mode)
            if not command.hide
        ]

    def formatted_aliases(self, mode: api.modes.Mode) -> List[Tuple[str, str]]:
        """Return list of aliases with explanation for this mode."""
        return [
            (f":{alias}", f"Alias for '{command}'")
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
        self.set_data(
            (f":!{api.completion.escape(cmd)}",)
            for cmd in executables
            if not cmd.startswith(".")
        )
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


class PathModel(api.completion.BaseModel):
    """Completion model filled with valid paths for path-like commands.

    Attributes:
        _command: The command for which this model is valid.
        _last_directory: Last directory to avoid re-evaluating on every character.
    """

    def __init__(self, command, valid_modes=api.modes.GLOBALS):
        super().__init__(f":{command} ", valid_modes=valid_modes)
        self._command = command
        self._directory_re = re.compile(rf"(: *{command} *)(.*)")
        self._last_directories = list()

    def on_enter(self, text: str) -> None:
        """Update completion options on enter."""
        self.on_text_changed(text)

    def on_text_changed(self, text: str) -> None:
        """Update completion options when text changes."""
        completion_terms = text.split()[1:]
        directories = list()
        for term in completion_terms:
            term = ':open ' + term
            directory = self._get_directory(term)
            directories.append(directory)
        # Nothing changed
        # for directory in directories:
        #     if os.path.realpath(directory) in self._last_directories:
        #         directories.remove(directory)
        # Prepare
        # self._last_directories = [ os.path.realpath(directory) for directory in directories ]
        # No completions for non-existent directory
        for directory in directories:
            if not os.path.isdir(os.path.expanduser(directory)):
                directories.remove(directory)
        total_images = list()
        total_directories = list()

        # Retrieve supported paths
        for directory in directories:
            images, directory_list = files.supported(files.listdir(directory))
            total_images.append(images)
            total_directories.append(directory_list)
        

        previous_completions = ['']
        for directory , images , directory_list in zip(directories,total_images,total_directories):
            completions = list()
            for previous in previous_completions:
                for path in images + directory_list:
                    if not previous:
                        completions.append(f"{os.path.join(directory,os.path.basename(path.strip()))}")
                    else:
                        completions.append(f"{previous.strip()} {os.path.join(directory,os.path.basename(path.strip()))}")
                    
            previous_completions.extend(completions)

        self.set_data([
            self._create_row(completion.split()) for completion in previous_completions
            if completion
                
            ])

    def _create_row(self,paths):
        row = [':' + self._command]
        for path in paths:
            row.append(api.completion.escape(path))
        return tuple([' '.join(row)])
        

    def _get_directory(self, text: str) -> str:
        """Retrieve directory for which the path completion is created."""
        match = self._directory_re.match(text)
        if not match:
            return "."
        _prefix, directory = match.groups()
        if "/" not in directory:
            if os.path.isdir(directory):
                return api.completion.unescape(directory)
            return "."
        return api.completion.unescape(os.path.dirname(directory))


class SettingsModel(api.completion.BaseModel):
    """Completion model filled with valid options for the :set command."""

    def __init__(self):
        super().__init__(":set ", column_widths=(0.4, 0.1, 0.5))
        self.set_data(
            (f":set {name}", str(setting), setting.desc)
            for name, setting in api.settings.items()
            if not setting.hidden
        )


class SettingsOptionModel(api.completion.BaseModel):
    """Completion model filled with suggestions for a specific setting.

    Attributes:
        _setting: The corresponding settings object.
    """

    def __init__(self, setting: api.settings.Setting):
        super().__init__(
            f":set {setting.name}", column_widths=(0.5, 0.5),
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
        self.set_data(
            (f":set {self._setting.name} {value}", option)
            for option, value in values.items()
        )

    def _on_changed(self, _value):
        """Update data if the value of the setting has changed."""
        self._update_data()


class TrashModel(api.completion.BaseModel):
    """Completion model filled with valid paths for the :undelete command."""

    def __init__(self):
        super().__init__(
            ":undelete ",
            column_widths=(0.4, 0.45, 0.15),
            valid_modes=api.modes.GLOBALS,
        )
        self._old_date_re = re.compile(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})(\d{2})")
        self._date_re = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})")

    def on_enter(self, text: str) -> None:
        """Update trash model on enter to include any newly un-/deleted paths."""
        data = []
        for path in files.listdir(trash_manager.files_directory()):
            cmd = f":undelete {api.completion.escape(os.path.basename(path))}"
            # Get info and format it neatly
            original, date = trash_manager.trash_info(path)
            original = original.replace(os.path.expanduser("~"), "~")
            original = os.path.dirname(original)
            date_match = self._date_re.match(date)
            if date_match is None:
                # Wrong date formatting that was used up to v0.7.0
                # TODO remove after releasing v1.0.0
                date_match = self._old_date_re.match(date)
            if date_match is not None:
                year, month, day, hour, minute, _ = date_match.groups()
                date = f"{year}-{month}-{day} {hour}:{minute}"
            else:
                date = "date unknown"
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
            f":{self._command} ", valid_modes=api.modes.GLOBALS,
        )

    def on_enter(self, text: str) -> None:
        """Update tag model on enter to include any new/deleted tags."""
        self.set_data(
            (f":{self._command} {api.completion.escape(fname)}",)
            for fname in files.listfiles(api.mark.tagdir)
        )


class HelpModel(api.completion.BaseModel):
    """Completion model filled with options for :help."""

    def __init__(self):
        super().__init__(":help", column_widths=(0.3, 0.7))
        self._general = [
            (":help  vimiv", "General information"),
            (":help  wildcards", "Information on various wildcards available"),
        ]
        self._formatted_settings = [
            (f":help {name}", setting.desc) for name, setting in api.settings.items()
        ]

    def on_enter(self, _text: str) -> None:
        """Create help list for appropriate mode when model is entered."""
        mode = api.modes.COMMAND.last
        self.set_data(
            self._general + self.formatted_commands(mode) + self._formatted_settings
        )

    @functools.lru_cache(len(api.modes.ALL) - 2)  # ALL without GLOBAL and COMMAND
    def formatted_commands(self, mode: api.modes.Mode) -> List[Tuple[str, str]]:
        """Return list of commands with description for this mode."""
        return [
            (f":help :{name}", command.description)
            for name, command in api.commands.items(mode)
        ]


def init():
    """Create completion models."""
    CommandModel()
    ExternalCommandModel()
    SettingsModel()
    for _, setting in api.settings.items():
        SettingsOptionModel(setting)
    for command in ("open", "delete", "mark"):
        PathModel(command)
    for suffix in ("delete", "load", "write", "open"):
        TagModel(suffix)
    TrashModel()
    HelpModel()
