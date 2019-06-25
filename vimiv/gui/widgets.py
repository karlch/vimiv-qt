# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Simple base QtWidgets to inherit from."""

from PyQt5.QtCore import QItemSelectionModel, QMargins, Qt
from PyQt5.QtGui import QPainter, QFontMetrics
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QTreeView,
    QAbstractItemView,
    QLabel,
    QSlider,
)

from vimiv.config import styles
from vimiv.utils import cached_method


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


class SliderWithValue(QSlider):
    """QSlider displaying the current value at the center.

    Attributes:
        _padding: Vertical padding in pixels between text and slider bar.
        _handle_margin: Vertical size the handle goes over the slider bar in pixels.
        _handle_width: Width of the handle in pixels.
    """

    STYLESHEET = ""  # Dummy that gets extended by custom dynamic styling

    PADDING = 2
    HANDLE_MARGIN = 5

    def __init__(self, left_color, handle_color, right_color, *args, parent=None):
        super().__init__(*args, parent=parent)
        self._left_color = left_color
        self._handle_color = handle_color
        self._right_color = right_color

    def paintEvent(self, event):
        """Override paint event to additionally paint the current value."""
        super().paintEvent(event)
        self._init_style()

        text = str(self.value())
        rect = self.geometry()
        painter = QPainter(self)
        font_metrics = QFontMetrics(self.font())

        x = (rect.width() - font_metrics.width(text)) / 2
        y = rect.height() - (rect.height() - font_metrics.capHeight()) / 2
        painter.drawText(x, y, text)

    @cached_method
    def _init_style(self):
        """Initialize the stylesheet.

        This is called on the first paintEvent to ensure all sizes and fonts are
        correct.
        """
        font_height = QFontMetrics(self.font()).capHeight()
        groove_height = font_height + 2 * self.PADDING
        total_height = groove_height + 2 * self.HANDLE_MARGIN
        sheet = f"""
        QSlider {{
            height: {total_height:d}px;
        }}

        QSlider::sub-page {{
            background-color: {self._left_color};
        }}

        QSlider::handle {{
            width: 24px;
            background-color: {self._handle_color};
            margin: -{SliderWithValue.HANDLE_MARGIN}px 0px;
        }}

        QSlider::groove {{
            background-color: {self._right_color};
            height: {groove_height}px;
        }}
        """
        styles.apply(self, append=sheet)


class ImageLabel(QLabel):
    """Label used to display images in image mode."""

    STYLESHEET = """
    QLabel {
        background-color: {image.bg};
    }
    """

    def __init__(self):
        super().__init__()
        styles.apply(self)
        self.setAlignment(Qt.AlignCenter)

    def current_size(self):
        """Return size of the currently displayed image."""
        raise NotImplementedError("Must be implemented by child widget")

    def original_size(self):
        """Return size of the original image."""
        raise NotImplementedError("Must be implemented by child widget")

    def rescale(self, scale):
        """Rescale the widget to scale."""
        raise NotImplementedError("Must be implemented by child widget")
