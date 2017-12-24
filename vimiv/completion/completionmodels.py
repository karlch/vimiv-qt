# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Models for the completion treeview in the command line."""

from vimiv.commands import commands
from vimiv.completion import completionbasemodel


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
        elem = (name, cmd.description.rstrip("."))
        cmdlist.append(elem)
    model.set_data(cmdlist)
    model.sort(0)
    return model
