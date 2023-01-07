# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Miscellaneous QtWidgets."""

from typing import Optional, Tuple

from vimiv.qt.core import Qt, QTimer
from vimiv.qt.gui import QPainter, QFontMetrics
from vimiv.qt.widgets import QTreeView, QAbstractItemView, QSlider, QDialog

from vimiv.config import styles
from vimiv.utils import cached_method


class ScrollToCenterMixin:
    """Mixin class to ensure the selected index stays at the center when scrolling."""

    def scrollTo(self, index, _hint=None):
        super().scrollTo(index, self.ScrollHint.PositionAtCenter)


class ScrollWheelCumulativeMixin:
    """Mixin class for cumulative mouse scrolling.

    Attributes:
        _callback: Function to call when an integer step is accumulated.
        _scroll_step: Currently unprocessed scrolling step to support finer devices.
        _scroll_timer: Timer to reset _scroll_step after scrolling.
    """

    def __init__(self, callback):
        self._callback = callback
        self._scroll_step_x = self._scroll_step_y = 0
        self._scroll_timer = QTimer()
        self._scroll_timer.setInterval(100)
        self._scroll_timer.setSingleShot(True)

        def reset_scroll_step():
            self._scroll_step_x = self._scroll_step_y = 0

        self._scroll_timer.timeout.connect(reset_scroll_step)

    def wheelEvent(self, event):
        """Update mouse wheel for proper scrolling.

        We accumulate steps until we have an integer value. For regular mice one "roll"
        should result in a single step. Finer grained devices such as touchpads need
        this cumulative approach.

        See https://doc.qt.io/qt-5/qwheelevent.html#angleDelta for more details.
        """
        self._scroll_step_x += event.angleDelta().x() / 120
        self._scroll_step_y += event.angleDelta().y() / 120

        steps_x = int(self._scroll_step_x)
        steps_y = int(self._scroll_step_y)

        if steps_x or steps_y:
            self._callback(steps_x, steps_y)

        self._scroll_step_x -= steps_x
        self._scroll_step_y -= steps_y
        self._scroll_timer.start()


class GetNumVisibleMixin:
    """Mixin class to get the number of visible items in a view."""

    def _visible_range(
        self, contains: bool = False
    ) -> Tuple[Optional[int], Optional[int]]:
        """Return index of first and last visible row."""
        index_first = index_last = None
        view_rect = self.viewport().rect()  # type: ignore[attr-defined]
        cutfunc = view_rect.contains if contains else view_rect.intersects
        for row in range(self.model().rowCount()):  # type: ignore[attr-defined]
            row_rect = self.visualRect(self.model().index(row, 0))  # type: ignore[attr-defined]  # pylint: disable=line-too-long,useless-suppression
            visible = cutfunc(row_rect)
            if visible:
                if index_first is None:
                    index_first = row
                index_last = row
        return index_first, index_last

    def _n_visible_items(self, *, contains=False) -> int:
        """Return the number of visible items in the view."""
        index_first, index_last = self._visible_range(contains=contains)
        if index_first is None or index_last is None:
            return 0
        return index_last - index_first


class FlatTreeView(ScrollToCenterMixin, QTreeView):
    """QTreeView without expandable items."""

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.setUniformRowHeights(True)
        self.setIndentation(0)
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        self.setItemsExpandable(False)
        self.setExpandsOnDoubleClick(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

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
        self.setCurrentIndex(index)

    def row(self):
        """Return the currently selected row."""
        return self.currentIndex().row()


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

        x = (rect.width() - font_metrics.horizontalAdvance(text)) // 2
        y = rect.height() - (rect.height() - font_metrics.capHeight()) // 2
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


class PopUp(QDialog):
    """Base class for pop-up windows to ensure consistent styling and behaviour."""

    STYLESHEET = """
    QDialog {
        background: {image.bg};
    }
    QLabel {
        color: {statusbar.fg};
        font: {library.font}
    }
    QPushButton {
        font: {statusbar.font};
        background-color: {statusbar.bg};
        border: 0px;
        padding: 4px;
        color: {statusbar.fg};
    }
    QPushButton:pressed {
        background-color: {library.selected.bg};
    }
    """

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.setWindowTitle(title)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.Tool)
        styles.apply(self)

    def reject(self):
        """Override reject to additionally delete the QObject."""
        super().reject()
        self.deleteLater()
