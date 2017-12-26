# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Thumbnail widget."""

import collections
import os

from PyQt5.QtCore import Qt, QSize, QItemSelectionModel
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from vimiv.commands import commands, argtypes
from vimiv.config import styles, keybindings
from vimiv.imutils.communicate import signals
from vimiv.modes import modehandler
from vimiv.gui import statusbar
from vimiv.utils import objreg, eventhandler, icon_creater, thumbnail_manager


class ThumbnailView(eventhandler.KeyHandler, QListWidget):
    """Thumbnail widget.

    Attributes:
        _stack: QStackedLayout containing image and thumbnail.
        _paths: Last paths loaded to avoid duplicate loading.
        _sizes: Dictionary of thumbnail sizes with integer size as key and
            string name of the size as value.
        _default_icon: QIcon to display before thumbnails were generated.
        _manager: ThumbnailManager class to create thumbnails asynchronously.
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
        self._sizes = collections.OrderedDict(
            [(64, "small"), (128, "normal"), (256, "large")])
        self._default_icon = icon_creater.default_thumbnail()
        self._manager = thumbnail_manager.ThumbnailManager()

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(256, 256))
        self.setResizeMode(QListWidget.Adjust)

        signals.paths_loaded.connect(self._on_paths_loaded)
        modehandler.signals.enter.connect(self._on_enter)
        modehandler.signals.leave.connect(self._on_leave)
        self._manager.created.connect(self._on_thumbnail_created)
        self.activated.connect(self._on_activated)

        styles.apply(self)

    def _on_paths_loaded(self, paths):
        """Load new paths into thumbnail widget.

        Args:
            paths: List of new paths to load.
        """
        if paths != self._paths:
            self._paths = paths
            self.clear()
            for _ in paths:
                item = QListWidgetItem(self._default_icon, None)
                item.setSizeHint(QSize(self.item_size(), self.item_size()))
                self.addItem(item)
            self._manager.create_thumbnails_async(paths)

    def _on_activated(self, index):
        """Emit signal to update image index on activated.

        Args:
            index: QModelIndex activated.
        """
        signals.update_index.emit(index.row() + 1)
        modehandler.enter("image")

    def _on_enter(self, widget):
        if widget == "thumbnail":
            self._stack.setCurrentWidget(self)
            self._select_item(0)

    def _on_leave(self, widget):
        # Need this here in addition to _on_enter in image because we may leave
        # for the library
        if widget == "thumbnail":
            self._stack.setCurrentWidget(objreg.get("image"))

    def _on_thumbnail_created(self, index, icon):
        """Insert created thumbnail as soon as manager created it.

        Args:
            index: Index of the created thumbnail as integer.
            icon: QIcon to insert.
        """
        self.takeItem(index)
        item = QListWidgetItem(icon, None)
        item.setSizeHint(QSize(self.item_size(), self.item_size()))
        self.insertItem(index, item)

    @keybindings.add("k", "scroll up", mode="thumbnail")
    @keybindings.add("j", "scroll down", mode="thumbnail")
    @keybindings.add("h", "scroll left", mode="thumbnail")
    @keybindings.add("l", "scroll right", mode="thumbnail")
    @commands.argument("direction", type=argtypes.scroll_direction)
    @commands.register(instance="thumbnail", mode="thumbnail", count=1)
    def scroll(self, direction, count):
        """Scroll thumbnails.

        Args:
            direction: One of "right", "left", "up", "down".
        """
        # print(self.columns())
        current = self.currentRow()
        if direction == "right":
            current += 1
        elif direction == "left":
            current -= 1
        elif direction == "down":
            current += self.columns()
        else:
            current -= self.columns()
        current = max(0, current)
        current = min(current, self.count() - 1)
        self._select_item(current)

    @keybindings.add("gg", "goto 1", mode="thumbnail")
    @keybindings.add("G", "goto -1", mode="thumbnail")
    @commands.argument("item", type=int)
    @commands.register(instance="thumbnail", mode="thumbnail", count=0)
    def goto(self, item, count):
        """Select thumbnail.

        Args:
            item: Number of the item to select if no count is given.
                -1 is the last item.
        """
        item = count if count else item  # Prefer count
        if item > 0:
            item -= 1  # Start indexing at 1
        item = item % self.count()
        self._select_item(item)

    @keybindings.add("-", "zoom out", mode="thumbnail")
    @keybindings.add("+", "zoom in", mode="thumbnail")
    @commands.argument("direction", type=argtypes.zoom)
    @commands.register(instance="thumbnail", mode="thumbnail")
    def zoom(self, direction):
        """Zoom thumbnails.

        Moves between the sizes in the self._sizes dictionary.

        Args:
            direction: One of "in", "out".
        """
        size = self.iconSize().width()
        size = size // 2 if direction == "out" else size * 2
        size = max(size, 64)
        size = min(size, 256)
        self.setIconSize(QSize(size, size))
        self.rescale_items()

    def rescale_items(self):
        """Reset item hint when item size has changed."""
        for i in range(self.count()):
            item = self.item(i)
            item.setSizeHint(QSize(self.item_size(), self.item_size()))

    def _select_item(self, index):
        """Select specific item in the ListWidget.

        Args:
            index: Number of the current item to select.
        """
        index = self.model().index(index, 0)
        self._select_index(index)

    def _select_index(self, index):
        """Select specific index in the ListWidget.

        Args:
            index: QModelIndex to select.
        """
        selmod = QItemSelectionModel.Rows | QItemSelectionModel.ClearAndSelect
        self.selectionModel().setCurrentIndex(index, selmod)

    def columns(self):
        """Return the number of columns."""
        padding = 2 * int(styles.get("thumbnail.padding"))
        return (self.width() - padding - 2) // self.item_size()

    def item_size(self):
        """Return the size of one icon including padding."""
        padding = int(styles.get("thumbnail.padding"))
        return self.iconSize().width() + 2 * padding

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
        return self._sizes[self.iconSize().width()]

    @statusbar.module("{thumbnail_index}", instance="thumbnail")
    def index(self):
        return str(self.currentRow() + 1)

    @statusbar.module("{thumbnail_total}", instance="thumbnail")
    def total(self):
        """Return the size of the thumbnails for the statusbar."""
        return str(self.model().rowCount())
