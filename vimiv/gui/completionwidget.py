# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Completion widget in the bar."""

from PyQt5.QtWidgets import QSizePolicy

from vimiv.config import styles, settings
from vimiv.gui import widgets
from vimiv.utils import objreg


class CompletionView(widgets.FlatTreeView):
    """Completion widget."""

    STYLESHEET = """
    QTreeView {
        font: {statusbar.font};
        color: {completion.fg};
        background-color: {completion.even.bg};
        alternate-background-color: {completion.odd.bg};
        outline: 0;
        border: 0px;
        padding: {statusbar.padding};
    }

    QTreeView::item:selected, QTreeView::item:selected:hover {
        color: {completion.selected.fg};
        background-color: {completion.selected.bg};
    }

    QTreeView QScrollBar {
        width: {completion.scrollbar.width};
        background: {completion.scrollbar.bg};
    }

    QTreeView QScrollBar::handle {
        background: {completion.scrollbar.fg};
        border: {completion.scrollbar.padding} solid
                {completion.scrollbar.bg};
        min-height: 10px;
    }

    QTreeView QScrollBar::sub-line, QScrollBar::add-line {
        border: none;
        background: none;
    }
    """

    @objreg.register("completion")
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setFixedHeight(settings.get_value("completion.height"))

        self.hide()

        styles.apply(self)

    def update_geometry(self, window_width, window_height):
        """Rescale width when main window was resized."""
        y = window_height - self.height()
        self.setGeometry(0, y, window_width, self.height())
