# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Simple QtWidgets."""

from PyQt5.QtCore import QMargins, Qt
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QTreeView,
                             QAbstractItemView)


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
