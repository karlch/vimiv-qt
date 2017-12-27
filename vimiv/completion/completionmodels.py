# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Models for the completion treeview in the command line."""

import os

from vimiv.commands import commands
from vimiv.completion import completionbasemodel
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
