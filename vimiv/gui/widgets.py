# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Simple QtWidgets."""

from PyQt5.QtCore import QItemSelectionModel, QMargins, Qt
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QTreeView,
                             QAbstractItemView, QLabel)

from vimiv.config import styles


class SimpleGrid(QGridLayout):
    """QGridLayout without spacing and margins."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(QMargins(0, 0, 0, 0))


class SimpleHBox(QHBoxLayout):
    """QHBoxLayout without spacing and margins."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(QMargins(0, 0, 0, 0))


class SimpleVBox(QVBoxLayout):
    """QVBoxLayout without spacing and margins."""

    def __init__(self, parent):
        super().__init__(parent)
        self.setSpacing(0)
        self.setContentsMargins(QMargins(0, 0, 0, 0))


class FlatTreeView(QTreeView):
    """QTreeView without expandable items."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.setUniformRowHeights(True)
        self.setIndentation(0)
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        self.setItemsExpandable(False)
        self.setExpandsOnDoubleClick(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _select_row(self, row):
        """Select a specific row in the library.

        Args:
            row: Number of the row to select.
        """
        index = self.model().index(row, 0)
        self._select_index(index)

    def _select_index(self, index):
        """Select a specific index in the library.

        Args:
            index: QModelIndex to select.
        """
        selmod = QItemSelectionModel.Rows | QItemSelectionModel.ClearAndSelect
        self.selectionModel().setCurrentIndex(index, selmod)

    def row(self):
        """Return the currently selected row."""
        selected_indexes = self.selectionModel().selectedIndexes()  # 3 columns
        return selected_indexes[0].row()


class ImageLabel(QLabel):
    """Label used to display images in image mode."""

    STYLESHEET = """
    QLabel {
        background-color: {image.bg};
    }
    """

    def __init__(self, parent):
        super().__init__(parent=parent)
        styles.apply(self)
        self.setAlignment(Qt.AlignCenter)
