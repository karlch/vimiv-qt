# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Simple QtWidgets."""

from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout


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
