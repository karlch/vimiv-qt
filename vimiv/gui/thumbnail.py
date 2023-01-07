# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Thumbnail widget."""

import contextlib
import math
import os
from typing import List, Optional, Iterator, cast

from vimiv.qt.core import Qt, QSize, QRect, pyqtSlot
from vimiv.qt.widgets import QListWidget, QListWidgetItem, QStyle, QStyledItemDelegate
from vimiv.qt.gui import QColor, QIcon

from vimiv import api, utils, imutils, widgets
from vimiv.commands import argtypes, search, number_for_command
from vimiv.config import styles
from vimiv.gui import eventhandler, synchronize
from vimiv.utils import create_pixmap, thumbnail_manager, log


_logger = log.module_logger(__name__)


# The class is certainly very border-line in size, much like the corresponding classes
# image.ScrollableImage and library.Library.
# TODO consider refactoring if this improves code-clarity
# pylint: disable=too-many-public-methods


class ThumbnailView(
    eventhandler.EventHandlerMixin,
    widgets.GetNumVisibleMixin,
    widgets.ScrollToCenterMixin,
    widgets.ScrollWheelCumulativeMixin,
    QListWidget,
):
    """Thumbnail widget.

    Attributes:
        _manager: ThumbnailManager class to create thumbnails asynchronously.
        _paths: Last paths loaded to avoid duplicate loading.
    """

    STYLESHEET = """
    QListWidget {
        font: {thumbnail.font};
        background-color: {thumbnail.bg};
    }

    QListWidget::item {
        padding: {thumbnail.padding}px;
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

    @api.modes.widget(api.modes.THUMBNAIL)
    @api.objreg.register
    def __init__(self) -> None:
        widgets.ScrollWheelCumulativeMixin.__init__(self, self._scroll_wheel_callback)
        QListWidget.__init__(self)

        self._paths: List[str] = []

        fail_pixmap = create_pixmap(
            color=styles.get("thumbnail.error.bg"),
            frame_color=styles.get("thumbnail.frame.fg"),
            size=256,
            frame_size=10,
        )
        self._manager = thumbnail_manager.ThumbnailManager(fail_pixmap)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewMode(QListWidget.IconMode)
        default_size = api.settings.thumbnail.size.value
        self.setIconSize(QSize(default_size, default_size))
        self.setResizeMode(QListWidget.Adjust)

        self.setItemDelegate(ThumbnailDelegate(self))
        self.setDragEnabled(False)

        api.signals.all_images_cleared.connect(self.clear)
        api.signals.new_image_opened.connect(self._select_path)
        api.signals.new_images_opened.connect(self._on_new_images_opened)
        api.settings.thumbnail.size.changed.connect(self._on_size_changed)
        search.search.new_search.connect(self._on_new_search)
        search.search.cleared.connect(self._on_search_cleared)
        self._manager.created.connect(self._on_thumbnail_created)
        self.activated.connect(self.open_selected)
        self.doubleClicked.connect(self.open_selected)
        api.mark.marked.connect(self._mark_highlight)
        api.mark.unmarked.connect(lambda path: self._mark_highlight(path, marked=False))
        api.mark.markdone.connect(self.repaint)
        synchronize.signals.new_library_path_selected.connect(self._select_path)

        styles.apply(self)

    def __iter__(self) -> Iterator["ThumbnailItem"]:
        for index in range(self.count()):
            yield self.item(index)

    def current_index(self) -> int:
        """Return the index of the currently selected item."""
        return self.currentRow()

    def current_column(self) -> int:
        """Return the column of the currently selected item."""
        return self.current_index() % self.n_columns()

    def current_row(self) -> int:
        """Return the row of the currently selected item."""
        return self.current_index() // self.n_columns()

    def n_columns(self) -> int:
        """Return the number of columns."""
        sb_width = int(styles.get("image.scrollbar.width").replace("px", ""))
        return (self.width() - sb_width) // self.item_size()

    def n_rows(self) -> int:
        """Return the number of rows."""
        return math.ceil(self.count() / self.n_columns())

    def item(self, index: int) -> "ThumbnailItem":
        return cast(ThumbnailItem, super().item(index))

    def clear(self):
        """Override clear to also empty paths."""
        self._paths = []
        super().clear()

    @pyqtSlot(list)
    def _on_new_images_opened(self, paths: List[str]):
        """Load new paths into thumbnail widget.

        Args:
            paths: List of new paths to load.
        """
        if paths == self._paths:  # Nothing to do
            _logger.debug("No new images to load")
            return
        _logger.debug("Updating thumbnails...")
        removed = set(self._paths) - set(paths)
        for path in removed:
            _logger.debug("Removing existing thumbnail '%s'", path)
            idx = self._paths.index(path)
            del self._paths[idx]  # Remove as the index also changes in the QListWidget
            if not self.takeItem(idx):
                _logger.error("Error removing thumbnail for '%s'", path)
        size_hint = QSize(self.item_size(), self.item_size())
        for i, path in enumerate(paths):
            if path not in self._paths:  # Add new path
                _logger.debug("Adding new thumbnail '%s'", path)
                ThumbnailItem(self, i, size_hint=size_hint)
            self.item(i).marked = path in api.mark.paths  # Ensure correct highlighting
        self._paths = paths
        self._manager.create_thumbnails_async(paths)
        _logger.debug("... update completed")

    @utils.slot
    def _on_thumbnail_created(self, index: int, icon: QIcon):
        """Insert created thumbnail as soon as manager created it.

        Args:
            index: Index of the created thumbnail as integer.
            icon: QIcon to insert.
        """
        item = self.item(index)
        if item is not None:  # Otherwise it has been deleted in the meanwhile
            item.setIcon(icon)

    @pyqtSlot(int, list, api.modes.Mode, bool)
    def _on_new_search(
        self, index: int, matches: List[str], mode: api.modes.Mode, _incremental: bool
    ):
        """Select search result after new search.

        Args:
            index: Index to select.
            matches: List of all matches of the search.
            mode: Mode for which the search was performed.
            _incremental: True if incremental search was performed.
        """
        if self._paths and mode == api.modes.THUMBNAIL:
            self._select_index(index)
            for item, path in zip(self, self._paths):
                item.highlighted = os.path.basename(path) in matches
            self.repaint()

    @utils.slot
    def _on_search_cleared(self):
        """Reset highlighted and force repaint when search results cleared."""
        for item in self:
            item.highlighted = False
        self.repaint()

    def _mark_highlight(self, path: str, marked: bool = True):
        """(Un-)Highlight a path if it was (un-)marked.

        Args:
            path: The (un-)marked path.
            marked: True if it was marked.
        """
        try:
            index = self._paths.index(path)
        except ValueError:
            _logger.debug("Ignoring mark as thumbnails have not been created")
            return
        item = self.item(index)
        item.marked = marked

    @api.commands.register(mode=api.modes.THUMBNAIL)
    def open_selected(self):
        """Open the currently selected thumbnail in image mode."""
        _logger.debug("Opening selected thumbnail '%s'", self.current())
        api.signals.load_images.emit([self.current()])
        api.modes.IMAGE.enter()

    @api.keybindings.register("<ctrl>b", "scroll page-up", mode=api.modes.THUMBNAIL)
    @api.keybindings.register("<ctrl>f", "scroll page-down", mode=api.modes.THUMBNAIL)
    @api.keybindings.register(
        "<ctrl>u", "scroll half-page-up", mode=api.modes.THUMBNAIL
    )
    @api.keybindings.register(
        "<ctrl>d", "scroll half-page-down", mode=api.modes.THUMBNAIL
    )
    @api.keybindings.register("k", "scroll up", mode=api.modes.THUMBNAIL)
    @api.keybindings.register("j", "scroll down", mode=api.modes.THUMBNAIL)
    @api.keybindings.register(
        ("h", "<button-back>"), "scroll left", mode=api.modes.THUMBNAIL
    )
    @api.keybindings.register(
        ("l", "<button-forward>"), "scroll right", mode=api.modes.THUMBNAIL
    )
    @api.commands.register(mode=api.modes.THUMBNAIL)
    def scroll(  # type: ignore[override]
        self, direction: argtypes.DirectionWithPage, count=1
    ):
        """Scroll to another thumbnail in the given direction.

        **syntax:** ``:scroll direction``

        positional arguments:
            * ``direction``: The direction to scroll in
              (left/right/up/down/page-up/page-down/half-page-up/half-page-down).

        **count:** multiplier
        """
        _logger.debug("Scrolling in direction '%s'", direction)
        current = self.current_index()
        if direction == direction.Right:
            current += count
        elif direction == direction.Left:
            current -= count
        else:
            current = self._scroll_updown(current, direction, count)
        self._select_index(current)

    def _scroll_updown(
        self, current: int, direction: argtypes.DirectionWithPage, step: int
    ) -> int:
        """Helper function bundling the logic required to scroll up/down."""
        if direction.is_page_step:
            n_items = self._n_visible_items(contains=True)
            factor = 0.5 if direction.is_half_page_step else 1
            n_rows = int(n_items / self.n_columns() * factor)
            step *= n_rows
        if direction.is_reverse:  # Upwards
            return max(self.current_column(), current - self.n_columns() * step)
        # Do not jump between columns
        last_in_col = (self.n_rows() - 1) * self.n_columns() + self.current_column()
        if last_in_col > self.count() - 1:
            last_in_col -= self.n_columns()
        return min(current + self.n_columns() * step, last_in_col)

    @api.keybindings.register("gg", "goto 1", mode=api.modes.THUMBNAIL)
    @api.keybindings.register("G", "goto -1", mode=api.modes.THUMBNAIL)
    @api.commands.register(mode=api.modes.THUMBNAIL)
    def goto(self, index: Optional[int], count: Optional[int] = None):
        """Select specific thumbnail in current filelist.

        **syntax:** ``:goto index``


        positional arguments:
            * ``index``: Number of the thumbnail to select.

        .. hint:: -1 is the last thumbnail.

        **count:** Select [count]th thubnail instead.
        """
        try:
            index = number_for_command(
                index, count, max_count=self.count(), elem_name="thumbnail"
            )
        except ValueError as e:
            raise api.commands.CommandError(str(e))
        self._select_index(index)

    @api.keybindings.register("$", "end-of-line", mode=api.modes.THUMBNAIL)
    @api.commands.register(mode=api.modes.THUMBNAIL)
    def end_of_line(self):
        """Select the last thumbnail in the current row."""
        first_in_next_row = (self.current_row() + 1) * self.n_columns()
        self._select_index(first_in_next_row - 1)

    @api.keybindings.register("^", "first-of-line", mode=api.modes.THUMBNAIL)
    @api.commands.register(mode=api.modes.THUMBNAIL)
    def first_of_line(self):
        """Select the first thumbnail in the current row."""
        self._select_index(self.current_row() * self.n_columns())

    @api.keybindings.register("-", "zoom out", mode=api.modes.THUMBNAIL)
    @api.keybindings.register("+", "zoom in", mode=api.modes.THUMBNAIL)
    @api.commands.register(mode=api.modes.THUMBNAIL)
    def zoom(self, direction: argtypes.Zoom):
        """Zoom the current widget.

        **syntax:** ``:zoom direction``

        positional arguments:
            * ``direction``: The direction to zoom in (in/out).

        **count:** multiplier
        """
        _logger.debug("Zooming in direction '%s'", direction)
        api.settings.thumbnail.size.step(up=direction == direction.In)

    def rescale_items(self):
        """Reset item hint when item size has changed."""
        for i in range(self.count()):
            item = self.item(i)
            item.setSizeHint(QSize(self.item_size(), self.item_size()))
        self.scrollTo(self.currentIndex())

    @utils.slot
    def _select_path(self, path: str):
        """Select a specific path by name."""
        with contextlib.suppress(ValueError):
            self._select_index(self._paths.index(path), emit=False)

    def _select_index(self, index: int, emit: bool = True) -> None:
        """Select specific item in the ListWidget.

        Args:
            index: Number of the current item to select.
            emit: Emit the new_thumbnail_path_selected signal.
        """
        if not self._paths:
            raise api.commands.CommandWarning("Thumbnail list is empty")
        _logger.debug("Selecting thumbnail number %d", index)
        index = utils.clamp(index, 0, self.count() - 1)
        self.setCurrentRow(index)
        if emit:
            synchronize.signals.new_thumbnail_path_selected.emit(self._paths[index])

    def _on_size_changed(self, value: int):
        _logger.debug("Setting size to %d", value)
        self.setIconSize(QSize(value, value))
        self.rescale_items()

    def item_size(self):
        """Return the size of one icon including padding."""
        padding = int(styles.get("thumbnail.padding").replace("px", ""))
        return self.iconSize().width() + 2 * padding

    @api.status.module("{thumbnail-basename}")
    def _thumbnail_basename(self):
        """Basename of the currently selected thumbnail."""
        try:
            abspath = self._paths[self.current_index()]
            basename = os.path.basename(abspath)
            return basename
        except IndexError:
            return ""

    @api.status.module("{thumbnail-name}")
    def _thumbnail_name(self):
        """Name without extension of the currently selected thumbnail."""
        try:
            name, _ = os.path.splitext(self._thumbnail_basename())
            return name
        except IndexError:
            return ""

    @api.status.module("{thumbnail-extension}")
    def _thumbnail_extension(self):
        """Extension of the currently selected thumbnail."""
        try:
            _, extension = os.path.splitext(self._thumbnail_basename())
            return extension.replace(".", "")
        except IndexError:
            return ""

    def current(self):
        """Current path for thumbnail mode."""
        try:
            return self._paths[self.current_index()]
        except IndexError:
            return ""

    @staticmethod
    def pathlist() -> List[str]:
        """List of current paths for thumbnail mode."""
        return imutils.pathlist()

    @api.status.module("{thumbnail-size}")
    def size(self):
        """Current thumbnail size (small/normal/large/x-large)."""
        sizes = {64: "small", 128: "normal", 256: "large", 512: "x-large"}
        return sizes[self.iconSize().width()]

    @api.status.module("{thumbnail-index}")
    def current_index_statusbar(self) -> str:
        """Index of the currently selected thumbnail."""
        return str(self.current_index() + 1).zfill(len(self.total()))

    @api.status.module("{thumbnail-total}")
    def total(self):
        """Total number of thumbnails."""
        return str(self.model().rowCount())

    def resizeEvent(self, event):
        """Update resize event to keep selected thumbnail centered."""
        super().resizeEvent(event)
        self.scrollTo(self.currentIndex())

    def _scroll_wheel_callback(self, steps_x, steps_y):
        """Callback function used by the scroll wheel mixin for mouse scrolling."""
        if steps_y < 0:
            self.scroll(argtypes.DirectionWithPage.Down, count=abs(steps_y))
        elif steps_y > 0:
            self.scroll(argtypes.DirectionWithPage.Up, count=steps_y)
        if steps_x < 0:
            self.scroll(argtypes.DirectionWithPage.Right, count=abs(steps_x))
        elif steps_x > 0:
            self.scroll(argtypes.DirectionWithPage.Left, count=steps_x)


class ThumbnailDelegate(QStyledItemDelegate):
    """Delegate used for the thumbnail widget.

    The delegate draws the items.
    """

    def __init__(self, parent):
        super().__init__(parent)

        # QColor options for background drawing
        self.bg = QColor(styles.get("thumbnail.bg"))
        self.selection_bg = QColor(styles.get("thumbnail.selected.bg"))
        self.selection_bg_unfocus = QColor(styles.get("thumbnail.selected.bg.unfocus"))
        self.search_bg = QColor(styles.get("thumbnail.search.highlighted.bg"))
        self.mark_bg = QColor(styles.get("mark.color"))
        self.padding = int(styles.get("thumbnail.padding"))

    def paint(self, painter, option, model_index):
        """Override the QStyledItemDelegate paint function.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            model_index: The QModelIndex.
        """
        item = self.parent().item(model_index.row())
        self._draw_background(painter, option, item)
        self._draw_pixmap(painter, option, item)

    def _draw_background(self, painter, option, item):
        """Draw the background rectangle of the thumbnail.

        The color depends on whether the item is selected and on whether it is
        highlighted as a search result.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            item: The ThumbnailItem.
        """
        color = self._get_background_color(item, option.state)
        painter.save()
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(option.rect)
        painter.restore()

    def _draw_pixmap(self, painter, option, item):
        """Draw the actual pixmap of the thumbnail.

        This calculates the size of the pixmap, applies padding and
        appropriately centers the image.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            item: The ThumbnailItem.
        """
        painter.save()
        # Original thumbnail pixmap
        pixmap = item.icon().pixmap(256)
        # Rectangle that can be filled by the pixmap
        rect = QRect(
            option.rect.x() + self.padding,
            option.rect.y() + self.padding,
            option.rect.width() - 2 * self.padding,
            option.rect.height() - 2 * self.padding,
        )
        # Size the pixmap should take
        size = pixmap.size().scaled(rect.size(), Qt.KeepAspectRatio)
        # Coordinates to center the pixmap
        diff_x = (rect.width() - size.width()) / 2.0
        diff_y = (rect.height() - size.height()) / 2.0
        x = int(option.rect.x() + self.padding + diff_x)
        y = int(option.rect.y() + self.padding + diff_y)
        # Draw
        painter.drawPixmap(x, y, size.width(), size.height(), pixmap)
        painter.restore()
        if item.marked:
            self._draw_mark(painter, option, x + size.width(), y + size.height())

    def _draw_mark(self, painter, option, x, y):
        """Draw small rectangle as mark indicator if the image is marked.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            x: x-coordinate at which the pixmap ends.
            y: y-coordinate at which the pixmap ends.
        """
        # Try to set 5 % of width, reduce to padding if this is smaller
        # At least 4px width
        width = int(max(min(0.05 * option.rect.width(), self.padding), 4))
        painter.save()
        painter.setBrush(self.mark_bg)
        painter.setPen(Qt.NoPen)
        painter.drawRect(x - width // 2, y - width // 2, width, width)
        painter.restore()

    def _get_background_color(self, item, state):
        """Return the background color of an item.

        The color depends on selected and highlighted as search result.

        Args:
            item: The ThumbnailItem storing highlight status.
            state: State of the model index indicating selected.
        """
        if state & QStyle.State_Selected:
            if api.modes.current() == api.modes.THUMBNAIL:
                return self.selection_bg
            return self.selection_bg_unfocus
        if item.highlighted:
            return self.search_bg
        return self.bg


class ThumbnailItem(QListWidgetItem):
    """Item storing a single thumbnail and it's search and mark status."""

    _default_icon = None

    def __init__(self, parent, index, *, size_hint, highlighted=False, marked=False):
        super().__init__(self.default_icon(), "", parent, index)
        self.highlighted = highlighted
        self.marked = marked
        self.setSizeHint(size_hint)

    @classmethod
    def default_icon(cls):
        """Default icon if the thumbnail has not been created.

        The return value is stored to avoid re-creating the pixmap for every thumbnail.
        """
        if cls._default_icon is None:
            cls._default_icon = cls.create_default_icon()
        return cls._default_icon

    @classmethod
    def create_default_icon(cls):
        """Create the default icon shown if the thumbnail has not been created."""
        return QIcon(
            create_pixmap(
                color=styles.get("thumbnail.default.bg"),
                frame_color=styles.get("thumbnail.frame.fg"),
                size=256,
                frame_size=10,
            )
        )
