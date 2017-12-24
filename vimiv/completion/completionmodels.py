# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Models for the completion treeview in the command line."""

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from vimiv.commands import commands


class CommandModel(QStandardItemModel):
    """Model used for internal commands.

    The model stores the rows.

    Attributes:
        column_widths: List of widths between 0 and 1 for every column.
    """

    def __init__(self, mode):
        super().__init__()
        self.column_widths = (0.3, 0.7)
        for name, command in commands.registry[mode].items():
            self._add_command(name, command.description.rstrip("."))
        self.sort(0)

    def _add_command(self, name, description):
        row = [QStandardItem(name), QStandardItem(description)]
        self.appendRow(row)
