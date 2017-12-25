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
