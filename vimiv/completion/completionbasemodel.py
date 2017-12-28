# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Base model used to create completion models."""

from PyQt5.QtGui import QStandardItemModel, QStandardItem


class BaseModel(QStandardItemModel):
    """Base model used for completion models.

    Attributes:
        column_widths: Tuple of floats [0..1] defining width of each column.
    """

    def __init__(self, column_widths=(1,)):
        super().__init__()
        self.column_widths = column_widths

    def set_data(self, data):
        """Add rows to the model.

        Args:
            data: List of tuples containing the data for each row.
        """
        for item in data:
            row = [QStandardItem(elem) for elem in item]
            self.appendRow(row)
