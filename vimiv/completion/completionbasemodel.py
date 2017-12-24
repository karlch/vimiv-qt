# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
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
        for item in data:
            row = [QStandardItem(elem) for elem in item]
            self.appendRow(row)
