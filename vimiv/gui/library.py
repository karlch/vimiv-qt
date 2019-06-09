# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Library widget with model and delegate."""

import logging
import os
from contextlib import suppress
from typing import List, Optional

from PyQt5.QtCore import Qt, QSize, QModelIndex, pyqtSlot
from PyQt5.QtWidgets import QStyledItemDelegate, QSizePolicy, QStyle
from PyQt5.QtGui import (
    QStandardItemModel,
    QColor,
    QTextDocument,
    QStandardItem,
    QFontMetrics,
    QFont,
)

from vimiv import api, utils, imutils
from vimiv.commands import argtypes, search
from vimiv.config import styles
from vimiv.gui import widgets
from vimiv.utils import (
    files,
    eventhandler,
    strip_html,
    clamp,
    working_directory,
    wrap_style_span,
)


class Library(eventhandler.KeyHandler, widgets.FlatTreeView):
    """Library widget.

    Attributes:
        _last_selected: Name of the path that was selected last.
        _positions: Dictionary that stores positions in directories.
    """

    STYLESHEET = """
    QTreeView {
        font: {library.font};
        color: {library.fg};
        background-color: {library.even.bg};
        alternate-background-color: {library.odd.bg};
        outline: 0;
        padding: {library.padding};
        border: 0px solid;
        border-right: {library.border};
    }

    QTreeView::item:selected, QTreeView::item:selected:hover {
        color: {library.selected.fg};
        background-color: {library.selected.bg};
    }

    QTreeView QScrollBar {
        width: {library.scrollbar.width};
        background: {library.scrollbar.bg};
    }

    QTreeView QScrollBar::handle {
        background: {library.scrollbar.fg};
        border: {library.scrollbar.padding} solid
                {library.scrollbar.bg};
        min-height: 10px;
    }

    QTreeView QScrollBar::sub-line, QScrollBar::add-line {
        border: none;
        background: none;
    }
    """

    @api.modes.widget(api.modes.LIBRARY)
    @api.objreg.register
    def __init__(self, mainwindow):
        super().__init__(parent=mainwindow)
        self._last_selected = ""
        self._positions = {}

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored)

        self.setModel(LibraryModel(self))
        self.setItemDelegate(LibraryDelegate())
        self.hide()

        self.activated.connect(self._on_activated)
        api.settings.library.width.changed.connect(self._on_width_changed)
        api.settings.library.show_hidden.changed.connect(self._on_show_hidden_changed)
        search.search.new_search.connect(self._on_new_search)
        search.search.cleared.connect(self._on_search_cleared)
        api.modes.LIBRARY.entered.connect(self._on_entered)
        api.modes.LIBRARY.left.connect(self._on_left)

        styles.apply(self)

    @utils.slot
    def _on_activated(self, index: QModelIndex):
        """Open path correctly on activate.

        If the path activated is an image, it is opened in image mode. If it is
        a directory, the library is loaded for this directory.

        Args:
            index: The QModelIndex activated.
        """
        self.open_selected()

    @pyqtSlot(int, list, api.modes.Mode, bool)
    def _on_new_search(
        self, index: int, matches: List[str], mode: api.modes.Mode, incremental: bool
    ):
        """Select search result after new search.

        Args:
            index: Index to select.
            matches: List of all matches of the search.
            mode: Mode for which the search was performed.
            incremental: True if incremental search was performed.
        """
        if mode == api.modes.LIBRARY:
            self._select_row(index)
            self.repaint()

    @utils.slot
    def _on_search_cleared(self):
        """Force repainting when the search results were cleared."""
        self.repaint()

    def _on_width_changed(self, _value: int):
        self.update_width()

    def _on_show_hidden_changed(self, _value: bool):
        self._open_directory(".", reload_current=True)

    @utils.slot
    def _on_entered(self):
        self.update_width()

    @utils.slot
    def _on_left(self):
        """Hide library widget if library mode was left."""
        self.hide()
        self._last_selected = ""

    @api.commands.register(mode=api.modes.LIBRARY)
    def open_selected(self, close: bool = False):
        """Open the currently selected path.

        If the path activated is an image, it is opened in image mode. If it is
        a directory, the library is loaded for this directory.

        **syntax:** ``:open-selected [--close]``

        optional arguments:
            * ``--close``: Close the library if an image was selected.
        """
        try:
            path_index = self.selectionModel().selectedIndexes()[1]
        # Path does not exist, do not try to select
        except IndexError:
            logging.warning("Library: selecting empty path")
            return
        path = strip(path_index.data())
        if os.path.isdir(path):
            self._open_directory(path)
        else:
            self._open_image(path, close)

    def _open_directory(self, path, reload_current=False):
        """Open a selected directory."""
        self.store_position()
        working_directory.handler.chdir(path, reload_current)

    def _open_image(self, path, close):
        """Open a selected image."""
        # Update image if a new image was selected
        if path != self._last_selected:
            imutils.load(path)
        # Close library on double selection or if specified
        close = close or path == self._last_selected
        self._last_selected = path
        if close:
            api.modes.LIBRARY.leave()

    @api.keybindings.register("k", "scroll up", mode=api.modes.LIBRARY)
    @api.keybindings.register("j", "scroll down", mode=api.modes.LIBRARY)
    @api.keybindings.register("h", "scroll left", mode=api.modes.LIBRARY)
    @api.keybindings.register("l", "scroll right", mode=api.modes.LIBRARY)
    @api.commands.register(mode=api.modes.LIBRARY)
    def scroll(self, direction: argtypes.Direction, count=1):
        """Scroll the library in the given direction.

        **syntax:** ``:scroll direction``

        The behaviour is similar to the file manager ranger.

        * Scrolling left selects the current file.
        * Scrolling right selects the parent directory.
        * Scrolling up and down moves the cursor.

        positional arguments:
            * ``direction``: The direction to scroll in (left/right/up/down).

        **count:** multiplier
        """
        if direction == direction.Right:
            self.open_selected()
        elif direction == direction.Left:
            self.store_position()
            working_directory.handler.chdir(os.pardir)
        else:
            try:
                row = self.row()
            # Directory is empty
            except IndexError:
                raise api.commands.CommandWarning("Directory is empty")
            if direction == direction.Up:
                row -= count
            else:
                row += count
            self._select_row(clamp(row, 0, self.model().rowCount() - 1))

    @api.keybindings.register("gg", "goto 1", mode=api.modes.LIBRARY)
    @api.keybindings.register("G", "goto -1", mode=api.modes.LIBRARY)
    @api.commands.register(mode=api.modes.LIBRARY)
    def goto(self, row: int, count: Optional[int] = None):
        """Select specific row in current filelist.

        **syntax:** ``:goto row``

        positional arguments:
            * ``row``: Number of the row to select.

        .. hint:: -1 is the last row.

        **count:** Select [count]th element instead.
        """
        if row == -1:
            row = self.model().rowCount()
        row = count if count is not None else row  # Prefer count
        if row > 0:
            row -= 1  # Start indexing at 1
        row = clamp(row, 0, self.model().rowCount() - 1)
        self._select_row(row)

    def update_width(self):
        """Resize width and columns when main window width changes."""
        width = self.parent().width() * api.settings.library.width.value
        self.setFixedWidth(width)
        self.setColumnWidth(0, 0.1 * width)
        self.setColumnWidth(1, 0.75 * width)
        self.setColumnWidth(2, 0.15 * width)

    def current(self):
        """Return absolute path of currently selected path."""
        with suppress(IndexError):  # No path selected
            basename = self.selectionModel().selectedIndexes()[1].data()
            basename = strip(basename)
            return os.path.abspath(basename)
        return ""

    def pathlist(self):
        """Return the list of currently open paths."""
        return self.model().pathlist()

    def store_position(self):
        """Set the stored position for a directory if possible."""
        with suppress(IndexError):
            self._positions[os.getcwd()] = self.row()

    def select_stored_position(self):
        """Select the stored position for a directory if possible."""
        directory = os.getcwd()
        row = (
            min(self._positions[directory], self.model().rowCount() - 1)
            if directory in self._positions
            else 0
        )  # Fallback to selecting the first row
        self._select_row(row)

    @staticmethod
    @api.commands.register(mode=api.modes.LIBRARY)
    def order(by: str = "name"):
        """Change image order.

        By default used order by name if --by is not specified.

        **syntax:** ``:order --by=modify``

        positional arguments:
            * ``by``: The name of an order function.
        """
        api.settings.image_order.value = by


class LibraryModel(QStandardItemModel):
    """Model used for the library.

    The model stores the rows and populates the row content when the working directory
    has changed.

    Attributes:
        _highlighted: List of indices that are highlighted as search results.
    """

    def __init__(self, parent):
        super().__init__(parent=parent)
        self._highlighted = []
        search.search.new_search.connect(self._on_new_search)
        search.search.cleared.connect(self._on_search_cleared)
        api.mark.marked.connect(self._mark_highlight)
        api.mark.unmarked.connect(lambda path: self._mark_highlight(path, marked=False))
        working_directory.handler.changed.connect(self._on_directory_changed)
        working_directory.handler.loaded.connect(self._update_content)

    @pyqtSlot(list, list)
    def _update_content(self, images: List[str], directories: List[str]):
        """Update library content with new images and directories.

        Args:
            images: Images in the current directory.
            directories: Directories in the current directory.
        """
        self.remove_all_rows()
        self._add_rows(directories, are_directories=True)
        self._add_rows(images, are_directories=False)
        self.parent().select_stored_position()

    @pyqtSlot(list, list)
    def _on_directory_changed(self, images: List[str], directories: List[str]):
        """Reload library when directory content has changed.

        In addition to _update_content() the position is stored.
        """
        self.parent().store_position()
        # This is tricky as we are calling a slot
        self._update_content(images, directories)  # type: ignore

    @pyqtSlot(int, list, api.modes.Mode, bool)
    def _on_new_search(
        self, index: int, matches: List[str], mode: api.modes.Mode, incremental: bool
    ):
        """Store list of indices to highlight on new search.

        Args:
            index: Index to select.
            matches: List of all matches of the search.
            mode: Mode for which the search was performed.
            incremental: True if incremental search was performed.
        """
        if mode == api.modes.LIBRARY:
            self._highlighted = []
            for i, path in enumerate(self.pathlist()):
                if os.path.basename(path) in matches:
                    self._highlighted.append(i)

    @utils.slot
    def _on_search_cleared(self):
        """Reset highlighted when the search results were cleared."""
        self._highlighted = []

    def _mark_highlight(self, path: str, marked: bool = True):
        """(Un-)Highlight a path if it was (un-)marked.

        Args:
            path: The (un-)marked path.
            marked: True if it was marked.
        """
        try:
            index = self.pathlist().index(path)
        except ValueError:
            return
        item = self.item(index, 1)
        item.setText(api.mark.highlight(item.text(), marked))

    def remove_all_rows(self):
        """Remove all rows from the model.

        This is implemented as a replacement for clear() which does not remove
        formatting.
        """
        self.removeRows(0, self.rowCount())

    def pathlist(self):
        """Return the list of currently open paths."""
        pathlist = []
        for i in range(self.rowCount()):
            basename = self.index(i, 1).data()
            basename = strip(basename)
            pathlist.append(os.path.abspath(basename))
        return pathlist

    def is_highlighted(self, index):
        """Return True if the index is highlighted as search result."""
        return index.row() in self._highlighted

    def _add_rows(self, paths: List[str], are_directories: bool = False):
        """Generate a library row for each path and add it to the model.

        Args:
            paths: List of paths to create a library row for.
            are_directories: Whether all paths are directories.
        """
        starting_index = self.rowCount() + 1  # Want to index from 1
        for i, path in enumerate(paths):
            name = os.path.basename(path)
            marked = path in api.mark.paths
            if are_directories:
                name = utils.add_html("b", name + "/")
            with suppress(FileNotFoundError):  # Has been deleted in the meantime
                size = files.get_size(path)
                self.appendRow(
                    (
                        QStandardItem(str(starting_index + i)),
                        QStandardItem(api.mark.highlight(name, marked)),
                        QStandardItem(size),
                    )
                )


class LibraryDelegate(QStyledItemDelegate):
    """Delegate used for the library.

    The delegate draws the items.
    """

    # Storing the styles makes the code more readable and faster IMHO
    # pylint: disable=too-many-instance-attributes
    def __init__(self):
        super().__init__()
        self.doc = QTextDocument(self)
        self.doc.setDocumentMargin(0)

        # Named properties for html
        self.font = styles.get("library.font")
        self.font_metrics = QFontMetrics(QFont(self.font))
        self.fg = styles.get("library.fg")
        self.dir_fg = styles.get("library.directory.fg")
        self.search_fg = styles.get("library.search.highlighted.fg")

        # QColor options for background drawing
        self.selection_bg = QColor()
        self.selection_bg.setNamedColor(styles.get("library.selected.bg"))
        self.even_bg = QColor()
        self.odd_bg = QColor()
        self.even_bg.setNamedColor(styles.get("library.even.bg"))
        self.odd_bg.setNamedColor(styles.get("library.odd.bg"))
        self.search_bg = QColor()
        self.search_bg.setNamedColor(styles.get("library.search.highlighted.bg"))

    def createEditor(self, *args):
        """Library is not editable by the user."""
        return None

    def paint(self, painter, option, index):
        """Override the QStyledItemDelegate paint function.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            index: The QModelIndex.
        """
        self._draw_background(painter, option, index)
        self._draw_text(painter, option, index)

    def _draw_text(self, painter, option, index):
        """Draw text for the library.

        Sets the font and the foreground color using html. The foreground color
        depends on whether the path is a directory and on whether it is
        highlighted as search result or not.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            index: The QModelIndex.
        """
        text = index.model().data(index)
        painter.save()
        color = self._get_foreground_color(index, text)
        text = self.elided(text, option.rect.width() - 1)
        text = wrap_style_span(f"color: {color}; font: {self.font}", text)
        self.doc.setHtml(text)
        self.doc.setTextWidth(option.rect.width() - 1)
        painter.translate(option.rect.x(), option.rect.y())
        self.doc.drawContents(painter)
        painter.restore()

    def _draw_background(self, painter, option, index):
        """Draw the background rectangle of the text.

        The color depends on whether the item is selected, in an even row or in
        an odd row.

        Args:
            painter: The QPainter.
            option: The QStyleOptionViewItem.
            index: The QModelIndex.
        """
        color = self._get_background_color(index, option.state)
        painter.save()
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(option.rect)
        painter.restore()

    def _get_foreground_color(self, index, text):
        """Return the foreground color of an item.

        The color depends on highlighted as search result and whether it is a
        directory.

        Args:
            index: Index of the element indicating even/odd/highlighted.
            text: Text indicating directory or not.
        """
        if index.model().is_highlighted(index):
            return self.search_fg
        return self.dir_fg if text.endswith("/") else self.fg

    def _get_background_color(self, index, state):
        """Return the background color of an item.

        The color depends on selected, highlighted as search result and
        even/odd.

        Args:
            index: Index of the element indicating even/odd/highlighted.
            state: State of the index indicating selected.
        """
        if state & QStyle.State_Selected:
            return self.selection_bg
        if index.model().is_highlighted(index):
            return self.search_bg
        if index.row() % 2:
            return self.odd_bg
        return self.even_bg

    def elided(self, text, width):
        """Return an elided text preserving html tags.

        If the text is wider than width, it is elided by replacing characters from the
        middle by …. Surrounding html tags are not included in the calculation and left
        untouched.

        Args:
            text: The text to elide.
            width: Width in pixels that the text may take.
        Returns:
            Elided version of the text.
        """
        mark_str = api.settings.statusbar.mark_indicator.value
        marked = text.startswith(mark_str)
        html_stripped = strip_html(text)
        elided = self.font_metrics.elidedText(html_stripped, Qt.ElideMiddle, width)
        # This becomes more complicated as the html is no longer simply surrounding
        # We must bring back the html from the mark indicator before replacing
        if marked:
            mark_stripped = strip_html(mark_str)
            html_stripped = html_stripped.replace(mark_stripped, mark_str)
            elided = elided.replace(mark_stripped, mark_str)
        return text.replace(html_stripped, elided)

    def sizeHint(self, option, index):
        """Return size of the QTextDocument as size hint."""
        text = wrap_style_span(f"font: {self.font}", "any")
        self.doc.setHtml(text)
        return QSize(self.doc.idealWidth(), self.doc.size().height())


def instance():
    return api.objreg.get(Library)


def strip(path: str) -> str:
    """Strip html tags and mark indicator from a library path."""
    return strip_html(api.mark.highlight(path, marked=False))
