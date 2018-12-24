# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Library widget with model and delegate."""

import logging
import os

from PyQt5.QtCore import Qt, QSize, pyqtSlot, QModelIndex
from PyQt5.QtWidgets import QStyledItemDelegate, QSizePolicy, QStyle
from PyQt5.QtGui import (QStandardItemModel, QStandardItem, QColor,
                         QTextDocument)

from vimiv.commands import commands, argtypes, cmdexc
from vimiv.config import styles, keybindings, settings
from vimiv.gui import widgets
from vimiv.imutils.imsignals import imsignals
from vimiv.modes import modehandler
from vimiv.utils import objreg, libpaths, eventhandler, misc, trash_manager


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

    @objreg.register("library")
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
        settings.signals.changed.connect(self._on_settings_changed)
        libpaths.signals.loaded.connect(self._on_paths_loaded)
        search = objreg.get("search")
        search.new_search.connect(self._on_new_search)
        search.cleared.connect(self._on_search_cleared)
        modehandler.signals.entered.connect(self._on_enter)
        modehandler.signals.left.connect(self._on_leave)
        trash_manager.signals.path_removed.connect(self._on_path_removed)
        trash_manager.signals.path_restored.connect(self._on_path_restored)
        imsignals.maybe_update_library.connect(self._on_maybe_update)

        styles.apply(self)

    @pyqtSlot(QModelIndex)
    def _on_activated(self, index):
        """Open path correctly on activate.

        If the path activated is an image, it is opened in image mode. If it is
        a directory, the library is loaded for this directory.

        Args:
            index: The QModelIndex activated.
        """
        try:
            path_index = self.selectionModel().selectedIndexes()[1]
        # Path does not exist, do not try to select
        except IndexError:
            logging.warning("library: selecting empty path")
            return
        path = misc.strip_html(path_index.data())
        # Open directory in library
        if os.path.isdir(path):
            self._positions[os.getcwd()] = self.row()
            libpaths.load(path)
        # Close library on double selection
        elif path == self._last_selected:
            modehandler.leave("library")
            self.hide()
            self._last_selected = ""
        # Update image
        else:
            imsignals.update_path.emit(os.path.abspath(path))
            self._last_selected = path

    @pyqtSlot(list)
    def _on_paths_loaded(self, data):
        """Fill library with paths when they were loaded.

        Args:
            images: List of images.
            directories: List of directories.
        """
        self.model().remove_all_rows()
        for i, row in enumerate(data):
            row = [QStandardItem(elem) for elem in row]
            row.insert(0, QStandardItem(str(i + 1)))
            self.model().appendRow(row)
        row = self._positions[os.getcwd()] \
            if os.getcwd() in self._positions \
            else 0
        self._select_row(row)

    @pyqtSlot(str)
    def _on_maybe_update(self, directory):
        """Possibly load library for new directory."""
        if not self.model().rowCount() or directory != os.getcwd():
            libpaths.load(directory)

    @pyqtSlot(int, list)
    def _on_new_search(self, index, matches):
        """Select search result after new search.

        Args:
            index: Index to select.
            matches: List of all matches of the search.
        """
        if self.hasFocus():
            self._select_row(index)

    @pyqtSlot()
    def _on_search_cleared(self):
        """Force repainting when the search results were cleared."""
        self.repaint()

    @pyqtSlot(str, object)
    def _on_settings_changed(self, setting, new_value):
        if setting == "library.width":
            self.update_width()

    @pyqtSlot(str)
    def _on_enter(self, widget):
        if widget == "library":
            self.show()
            self.update_width()

    @pyqtSlot(str)
    def _on_leave(self, widget):
        if widget == "library":
            self.hide()

    @keybindings.add("k", "scroll up", mode="library")
    @keybindings.add("j", "scroll down", mode="library")
    @keybindings.add("h", "scroll left", mode="library")
    @keybindings.add("l", "scroll right", mode="library")
    @commands.argument("direction", type=argtypes.scroll_direction)
    @commands.register(instance="library", mode="library", count=1)
    def scroll(self, direction, count):
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
        if direction == "right":
            self.activated.emit(self.selectionModel().currentIndex())
        elif direction == "left":
            try:
                self._positions[os.getcwd()] = self.row()
            # Do not store empty positions
            except IndexError:
                pass
            libpaths.load("..")
        else:
            try:
                row = self.row()
            # Directory is empty
            except IndexError:
                raise cmdexc.CommandWarning("Directory is empty")
            if direction == "up":
                row -= count
            else:
                row += count
            self._select_row(misc.clamp(row, 0, self.model().rowCount() - 1))

    @keybindings.add("gg", "goto 1", mode="library")
    @keybindings.add("G", "goto -1", mode="library")
    @commands.argument("row", type=int)
    @commands.register(instance="library", mode="library", count=0)
    def goto(self, row, count):
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
        row = misc.clamp(row, 0, self.model().rowCount() - 1)
        self._select_row(row)

    def update_width(self):
        """Resize width and columns when main window width changes."""
        width = self.parent().width() * \
            settings.get_value(settings.Names.LIBRARY_WIDTH)
        self.setFixedWidth(width)
        self.setColumnWidth(0, 0.1 * width)
        self.setColumnWidth(1, 0.75 * width)
        self.setColumnWidth(2, 0.15 * width)

    def current(self):
        """Return absolute path of currently selected path."""
        try:
            basename = self.selectionModel().selectedIndexes()[1].data()
            basename = misc.strip_html(basename)
            return os.path.abspath(basename)
        except IndexError:
            return ""

    def pathlist(self):
        """Return the list of currently open paths."""
        return self.model().pathlist()

    @pyqtSlot(str)
    def _on_path_removed(self, path):
        """Clear path from library on deletion."""
        if path in self.model().pathlist():
            row = self.model().pathlist().index(path)
            self.model().removeRows(row, 1)

    @pyqtSlot(str)
    def _on_path_restored(self, path):
        """Reload library if restored path is in the current directory."""
        if os.path.dirname(path) == os.getcwd():
            self._positions[os.getcwd()] = self.row()
            libpaths.load(".")


class LibraryModel(QStandardItemModel):
    """Model used for the library.

    The model stores the rows.

    Attributes:
        _highlighted: List of indices that are highlighted as search results.
    """

    def __init__(self):
        super().__init__()
        self._highlighted = []
        search = objreg.get("search")
        search.new_search.connect(self._on_new_search)
        search.cleared.connect(self._on_search_cleared)

    @pyqtSlot(int, list)
    def _on_new_search(self, index, matches):
        """Store list of indices to highlight on new search.

        Args:
            index: Index that will be selected.
            matches: List of all matches of the search.
        """
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
            basename = misc.strip_html(basename)
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
