# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Completion widget in the bar."""

from PyQt5.QtCore import pyqtSignal, Qt

from vimiv import api, widgets
from vimiv.config import styles


class CompletionView(widgets.FlatTreeView):
    """Completion widget.

    Signals:
        activated: Emitted when the complete command was called.
            arg1: The selected completion text.
    """

    STYLESHEET = """
    QTreeView {
        font: {statusbar.font};
        color: {completion.fg};
        background-color: {completion.even.bg};
        alternate-background-color: {completion.odd.bg};
        outline: 0;
        border: 0px;
        min-height: {completion.height};
        max-height: {completion.height};
    }

    QTreeView::item:selected, QTreeView::item:selected:hover {
        color: {completion.selected.fg};
        background-color: {completion.selected.bg};
    }
    """

    activated = pyqtSignal(str)

    @api.objreg.register
    def __init__(self, parent):
        super().__init__(parent=parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setEditTriggers(self.NoEditTriggers)
        self.setModel(api.completion.FilterProxyModel())

        styles.apply(self)

    @api.keybindings.register(
        "<shift><tab>", "complete --inverse", mode=api.modes.COMMAND
    )
    @api.keybindings.register("<tab>", "complete", mode=api.modes.COMMAND)
    @api.commands.register(mode=api.modes.COMMAND)
    def complete(self, inverse: bool = False):
        """Invoke command line completion.

        **syntax:** ``:complete [--inverse]``

        optional arguments:
            * ``--inverse``: Complete in inverse direction.
        """
        if self.row() == -1:  # First trigger of completion
            row = -1 if inverse else 0
        else:
            row = self.row() - 1 if inverse else self.row() + 1
        # No suggestions
        if not self.model().rowCount():
            return
        row = row % self.model().rowCount()
        self._select_row(row)
        index = self.currentIndex()
        completion = index.data()
        self.activated.emit(completion.lstrip())

    def resizeEvent(self, event):
        """Resize columns on resize event."""
        super().resizeEvent(event)
        self.update_column_widths()

    def update_column_widths(self):
        """Resize columns according to model."""
        for i in range(self.model().columnCount()):
            fraction = self.model().sourceModel().column_widths[i]
            self.setColumnWidth(i, int(fraction * self.width()))
