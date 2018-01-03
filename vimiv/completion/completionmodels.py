# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Models for the completion treeview in the command line."""

import os

from vimiv.commands import commands, aliases
from vimiv.completion import completionbasemodel
from vimiv.config import settings as vimivsettings  # Modelfunc called settings
from vimiv.utils import files


def command(mode):
    """Completion model filled with commands and descriptions.

    Args:
        mode: Mode for which commands are valid.
    Return:
        The generated completion model.
    """
    model = completionbasemodel.BaseModel(column_widths=(0.3, 0.7))
    cmdlist = []
    for name, cmd in commands.registry[mode].items():
        if not cmd.hide:
            elem = (name, cmd.description)
            cmdlist.append(elem)
    for alias, cmd in aliases.get(mode).items():
        desc = "Alias for '%s'." % (cmd)
        cmdlist.append((alias, desc))
    model.set_data(cmdlist)
    model.sort(0)
    return model


def paths(text):
    """Completion model filled with valid paths for the :open command.

    Args:
        text: Text in the command line after :open used to find directory.
    Return:
        The generated completion model.
    """
    model = completionbasemodel.BaseModel()
    # Get directory
    if not text:
        directory = "."
    elif "/" not in text:
        directory = text if os.path.isdir(text) else "."
    else:
        directory = os.path.dirname(text)
    # Empty model for non-existent directories
    if not os.path.isdir(os.path.expanduser(directory)):
        return model
    # Get supported paths
    pathlist = []
    images, directories = files.get_supported(files.ls(directory))
    pathlist.extend(images)
    pathlist.extend(directories)
    # Format data
    data = []
    for path in pathlist:
        path = os.path.join(directory, os.path.basename(path))
        data.append(["open %s" % (path)])
    model.set_data(data)
    return model


def settings(text):
    """Completion model filled with valid options for the :set command.

    Args:
        text: Text in the command line after :set used to find values.
    Return:
        The generated completion model.
    """
    data = []
    # Show valid options for the setting
    if text in vimivsettings.names():
        model = completionbasemodel.BaseModel((0.5, 0.5))
        setting = vimivsettings.get(text)
        values = {
            "default": str(setting.get_default()),
            "current": str(setting.get_value())
        }
        for i, suggestion in enumerate(setting.suggestions()):
            values["suggestion %d" % (i + 1)] = suggestion
        for name, value in values.items():
            data.append(("set %s %s" % (text, value), name))
    # Show all settings
    else:
        model = completionbasemodel.BaseModel((0.4, 0.1, 0.5))
        for name, setting in vimivsettings.items():
            cmd = "set %s" % (name)
            data.append((cmd, str(setting), setting.desc))
    model.set_data(data)
    return model


class ExternalCommandModel(completionbasemodel.BaseModel):
    """Completion model filled with shell executables for :!."""

    def __init__(self):
        super().__init__()
        executables = self._get_executables()
        data = [["!%s" % (cmd)]
                for cmd in executables
                if not cmd.startswith(".")]
        self.set_data(data)

    def _get_executables(self):
        """Return ordered list of shell executables.

        Thanks to aszlig https://github.com/aszlig who wrote the initial
        version of this for the Gtk version of vimiv.
        """
        pathenv = os.environ.get('PATH')
        if pathenv is not None:
            pathdirs = [d for d in pathenv.split(":") if os.path.isdir(d)]
            executables = set()
            for bindir in pathdirs:
                executables |= set(os.listdir(bindir))
            external_commands = sorted(list(executables))
        else:
            external_commands = []
        return external_commands


# Only generate list of executables once
_external_command_model = ExternalCommandModel()


def external():
    """Completion model filled with external commands for :!.

    Return:
        The generated completion model.
    """
    return _external_command_model
