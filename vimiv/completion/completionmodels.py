# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Models for the completion treeview in the command line."""

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from vimiv.commands import commands


class CommandModel(QStandardItemModel):
    """Model used for internal commands.

    The model stores the rows.
    """

    def __init__(self, mode):
        super().__init__()
        for name, command in commands.registry[mode].items():
            self._add_command(name, command.description.rstrip("."))

    def _add_command(self, name, description):
        row = [QStandardItem(name), QStandardItem(description)]
        self.appendRow(row)
