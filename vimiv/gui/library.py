# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Library widget with model and delegate."""

import logging
import os

from PyQt5.QtCore import Qt, QSize, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QStyledItemDelegate, QSizePolicy, QStyle
from PyQt5.QtGui import QStandardItemModel, QColor, QTextDocument

from vimiv import api
from vimiv.commands import argtypes, search
from vimiv.config import styles
from vimiv.gui import widgets
from vimiv.imutils.imsignals import imsignals
from vimiv.utils import (libpaths, eventhandler, strip_html, clamp,
                         working_directory, ignore)


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

        self.setModel(LibraryModel())
        self.setItemDelegate(LibraryDelegate())
        self.hide()

        self.activated.connect(self._on_activated)
        api.settings.signals.changed.connect(self._on_settings_changed)
        libpaths.handler.loaded.connect(self._on_paths_loaded)
        libpaths.handler.changed.connect(self._on_paths_changed)
        search.search.new_search.connect(self._on_new_search)
        search.search.cleared.connect(self._on_search_cleared)
        api.modes.signals.entered.connect(self._on_mode_entered)
        api.modes.signals.left.connect(self._on_mode_left)

        styles.apply(self)

    @pyqtSlot(QModelIndex)
    def _on_activated(self, index):
        """Open path correctly on activate.

        If the path activated is an image, it is opened in image mode. If it is
        a directory, the library is loaded for this directory.

        Args:
            index: The QModelIndex activated.
        """
        self.open_selected()

    @pyqtSlot(list)
    def _on_paths_loaded(self, data):
        """Fill library with paths when they were loaded.

        Args:
            data: List of data defining the content of the library.
        """
        self._set_content(data)

    @pyqtSlot(list)
    def _on_paths_changed(self, data):
        """Reload library with paths when they changed.

        Args:
            data: List of data defining the content of the library.
        """
        self._store_position()
        self._set_content(data)

    @pyqtSlot(int, list, api.modes.Mode, bool)
    def _on_new_search(self, index, matches, mode, incremental):
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

    @pyqtSlot()
    def _on_search_cleared(self):
        """Force repainting when the search results were cleared."""
        self.repaint()

    @pyqtSlot(api.settings.Setting)
    def _on_settings_changed(self, setting):
        if setting == api.settings.LIBRARY_WIDTH:
            self.update_width()

    @pyqtSlot(api.modes.Mode, api.modes.Mode)
    def _on_mode_entered(self, mode, last_mode):
        """Show or hide library depending on the mode entered.

        Args:
            mode: The mode entered.
            last_mode: The mode left.
        """
        if mode == api.modes.LIBRARY:
            self.show()
            self.update_width()

    @pyqtSlot(api.modes.Mode)
    def _on_mode_left(self, mode):
        """Hide library widget if library mode was left.

        Args:
            mode: The mode left.
        """
        if mode == api.modes.LIBRARY:
            self.hide()
            self._last_selected = ""

    def _set_content(self, data):
        """Set content of the library to data."""
        self.model().remove_all_rows()
        for row in data:
            self.model().appendRow(row)
        row = self._get_stored_position(os.getcwd())
        self._select_row(row)

    @api.commands.register(mode=api.modes.LIBRARY)
    def open_selected(self, close: bool = False):
        """Open the currently selected path.

        If the path activated is an image, it is opened in image mode. If it is
        a directory, the library is loaded for this directory.

        **syntax:** ``:open-selected [--close]``

        optional arguments:
            * ``close``: Close the library if an image was selected.
        """
        try:
            path_index = self.selectionModel().selectedIndexes()[1]
        # Path does not exist, do not try to select
        except IndexError:
            logging.warning("library: selecting empty path")
            return
        path = strip_html(path_index.data())
        if os.path.isdir(path):
            self._open_directory(path)
        else:
            self._open_image(path, close)

    def _open_directory(self, path):
        """Open a selected directory."""
        self._store_position()
        working_directory.handler.chdir(path)

    def _open_image(self, path, close):
        """Open a selected image."""
        # Update image if a new image was selected
        if path != self._last_selected:
            imsignals.open_new_image.emit(path)
        # Close library on double selection or if specified
        close = (close or path == self._last_selected)
        self._last_selected = path
        if close:
            api.modes.leave(api.modes.LIBRARY)

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
            with ignore(IndexError):  # Do not store empty positions
                self._positions[os.getcwd()] = self.row()
            working_directory.handler.chdir("..")
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
    def goto(self, row: int, count: int = 0):
        """Select specific row in current filelist.

        **syntax:** ``:goto row``

        positional arguments:
            * ``row``: Number of the row to select.

        .. hint:: -1 is the last row.

        **count:** Select [count]th element instead.
        """
        if row == - 1:
            row = self.model().rowCount()
        row = count if count else row  # Prefer count
        if row > 0:
            row -= 1  # Start indexing at 1
        row = clamp(row, 0, self.model().rowCount() - 1)
        self._select_row(row)

    def update_width(self):
        """Resize width and columns when main window width changes."""
        width = self.parent().width() * api.settings.LIBRARY_WIDTH.value
        self.setFixedWidth(width)
        self.setColumnWidth(0, 0.1 * width)
        self.setColumnWidth(1, 0.75 * width)
        self.setColumnWidth(2, 0.15 * width)

    def current(self):
        """Return absolute path of currently selected path."""
        with ignore(IndexError):
            basename = self.selectionModel().selectedIndexes()[1].data()
            basename = strip_html(basename)
            return os.path.abspath(basename)
        return ""

    def pathlist(self):
        """Return the list of currently open paths."""
        return self.model().pathlist()

    def _store_position(self):
        """Set the stored position for a directory if possible."""
        if self.model().rowCount():
            self._positions[os.getcwd()] = self.row()

    def _get_stored_position(self, directory):
        """Return the stored position for a directory if possible."""
        if directory not in self._positions:
            return 0
        return min(self._positions[directory], self.model().rowCount() - 1)


class LibraryModel(QStandardItemModel):
    """Model used for the library.

    The model stores the rows.

    Attributes:
        _highlighted: List of indices that are highlighted as search results.
    """

    def __init__(self):
        super().__init__()
        self._highlighted = []
        search.search.new_search.connect(self._on_new_search)
        search.search.cleared.connect(self._on_search_cleared)

    @pyqtSlot(int, list, api.modes.Mode, bool)
    def _on_new_search(self, index, matches, mode, incremental):
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

    @pyqtSlot()
    def _on_search_cleared(self):
        """Reset highlighted when the search results were cleared."""
        self._highlighted = []

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
            basename = strip_html(basename)
            pathlist.append(os.path.abspath(basename))
        return pathlist

    def is_highlighted(self, index):
        """Return True if the index is highlighted as search result."""
        return index.row() in self._highlighted


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
        self.search_bg.setNamedColor(
            styles.get("library.search.highlighted.bg"))

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
        text = '<span style="color: %s; font: %s;">%s</span>' \
            % (color, self.font, text)
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

    def sizeHint(self, option, index):
        """Return size of the QTextDocument as size hint."""
        text = '<span style="font: %s;">any</>' % (self.font)
        self.doc.setHtml(text)
        return QSize(self.doc.idealWidth(), self.doc.size().height())


def instance():
    return api.objreg.get(Library)
