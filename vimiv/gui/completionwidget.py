# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Completion widget in the bar."""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSizePolicy

from vimiv.commands import commands
from vimiv.completion import completionmodels, completionfilters
from vimiv.config import styles, settings, keybindings
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

    activated = pyqtSignal(str)

    @objreg.register("completion")
    def __init__(self, parent):
        super().__init__(parent=parent)
        self.proxy_model = completionfilters.TextFilter()
        self.setModel(self.proxy_model)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setFixedHeight(settings.get_value("completion.height"))

        self.hide()

        styles.apply(self)

    def update_geometry(self, window_width, window_height):
        """Rescale width when main window was resized."""
        y = window_height - self.height()
        self.setGeometry(0, y, window_width, self.height())

    def init(self, mode):
        """Initialize completion for commands.

        Args:
            mode: Mode for which commands are filtered.
        """
        source_model = completionmodels.CommandModel(mode)
        self.proxy_model.setSourceModel(source_model)
        self.show()

    @keybindings.add("shift+tab", "complete --inverse", mode="command")
    @keybindings.add("tab", "complete", mode="command")
    @commands.argument("inverse", optional=True, action="store_true")
    @commands.register(instance="completion", mode="command")
    def complete(self, inverse):
        """Invoke command line completion."""
        try:
            row = self.row() - 1 if inverse else self.row() + 1
        except IndexError:  # First trigger of completion
            row = -1 if inverse else 0
        row = row % self.model().rowCount()
        self._select_row(row)
        command_index = self.selectionModel().selectedIndexes()[0]
        command = command_index.data()
        self.activated.emit(command)

    def resizeEvent(self, event):
        """Resize columns on resize event."""
        super().resizeEvent(event)
        for i in range(self.model().columnCount()):
            fraction = self.model().sourceModel().column_widths[i]
            self.setColumnWidth(i, fraction * self.width())
