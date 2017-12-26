# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Thumbnail widget."""

import os

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtGui import QIcon

from vimiv.config import styles
from vimiv.modes import modehandler
from vimiv.gui import statusbar
from vimiv.utils import impaths, objreg, eventhandler


class ThumbnailView(eventhandler.KeyHandler, QListWidget):
    """Thumbnail widget.

    Attributes:
        _stack: QStackedLayout containing image and thumbnail.
        _paths: Last paths loaded to avoid duplicate loading.
    """

    STYLESHEET = """
    QListWidget {
        font: {thumbnail.font};
        background-color: {thumbnail.bg};
    }

    QListWidget::item {
        padding: {thumbnail.padding}px;
        color: {thumbnail.fg};
        background: {thumbnail.bg}
    }

    QListWidget::item:selected {
        background: {thumbnail.selected.bg};
    }

    QListWidget QScrollBar {
        width: {library.scrollbar.width};
        background: {library.scrollbar.bg};
    }

    QListWidget QScrollBar::handle {
        background: {library.scrollbar.fg};
        border: {library.scrollbar.padding} solid
                {library.scrollbar.bg};
        min-height: 10px;
    }

    QListWidget QScrollBar::sub-line, QScrollBar::add-line {
        border: none;
        background: none;
    }
    """

    @objreg.register("thumbnail")
    def __init__(self, stack):
        super().__init__()
        self._stack = stack
        self._paths = []

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(256, 256))
        self.setUniformItemSizes(True)
        self.setResizeMode(QListWidget.Adjust)

        impaths.signals.new_paths.connect(self._on_new_paths)
        modehandler.signals.enter.connect(self._on_enter)
        modehandler.signals.leave.connect(self._on_leave)

        styles.apply(self)

    def _on_new_paths(self, paths):
        """Load new paths into thumbnail widget.

        Args:
            paths: List of new paths to load.
        """
        if paths != self._paths:
            self._paths = paths
            self.clear()
            for path in paths:
                item = QListWidgetItem(QIcon(path), None)
                self.addItem(item)

    def _on_enter(self, widget):
        if widget == "thumbnail":
            self._stack.setCurrentWidget(self)

    def _on_leave(self, widget):
        # Need this here in addition to _on_enter in image because we may leave
        # for the library
        if widget == "thumbnail":
            self._stack.setCurrentWidget(objreg.get("image"))

    @statusbar.module("{thumbnail_name}", instance="thumbnail")
    def current(self):
        """Return the name of the current thumbnail for the statusbar."""
        try:
            abspath = self._paths[self.currentRow()]
            basename = os.path.basename(abspath)
            name, _ = os.path.splitext(basename)
            return name
        except IndexError:
            return ""

    @statusbar.module("{thumbnail_size}", instance="thumbnail")
    def size(self):
        """Return the size of the thumbnails for the statusbar."""
        size = self.iconSize().width()
        if size == 64:
            return "small"
        elif size == 128:
            return "normal"
        else:
            return "large"

    @statusbar.module("{thumbnail_index}", instance="thumbnail")
    def index(self):
        return str(self.currentRow() + 1)

    @statusbar.module("{thumbnail_total}", instance="thumbnail")
    def total(self):
        """Return the size of the thumbnails for the statusbar."""
        return str(self.model().rowCount())
