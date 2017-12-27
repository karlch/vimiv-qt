# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Library widget with model and delegate."""

import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

from vimiv.commands import commands, argtypes, cmdexc
from vimiv.config import styles, keybindings, settings
from vimiv.gui import widgets
from vimiv.imutils import imcommunicate
from vimiv.modes import modehandler
from vimiv.utils import objreg, libpaths, eventhandler


class Library(eventhandler.KeyHandler, widgets.FlatTreeView):
    """Library widget.

    Attributes:
        _last_selected: Name of the path that was selected last.
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
    def __init__(self):
        super().__init__()
        self._last_selected = ""

        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Ignored)

        model = LibraryModel()
        self.setModel(model)
        self.setItemDelegate(LibraryDelegate())
        self.hide()

        width = settings.get_value("library.width")
        self.setFixedWidth(width)
        self.setColumnWidth(0, 0.1 * width)
        self.setColumnWidth(1, 0.7 * width)
        self.setColumnWidth(2, 0.2 * width)

        self.activated.connect(self._on_activated)
        settings.signals.changed.connect(self._on_settings_changed)
        libpaths.signals.loaded.connect(self._on_paths_loaded)
        modehandler.signals.enter.connect(self._on_enter)
        modehandler.signals.leave.connect(self._on_leave)
        imcommunicate.signals.maybe_update_library.connect(self._on_maybe_update)

        styles.apply(self)

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
            return
        path = path_index.data()
        # Open directory in library
        if os.path.isdir(path):
            libpaths.load(path)
        # Close library and enter image mode on double selection
        elif path == self._last_selected:
            modehandler.enter("image")
            self.hide()
            self._last_selected = ""
        # Update image
        else:
            imcommunicate.signals.update_path.emit(os.path.abspath(path))
            self._last_selected = path

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
        self._select_row(0)

    def _on_maybe_update(self, directory):
        """Possibly load library for new directory."""
        if not self.model().rowCount() or directory != os.getcwd():
            libpaths.load(directory)

    def _on_settings_changed(self, setting, new_value):
        if setting == "library.width":
            self.setFixedWidth(new_value)

    def _on_enter(self, widget):
        if widget == "library":
            self.show()

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
        """Scroll the library.

        Args:
            direction: One of "right", "left", "up", "down".
        """
        if direction == "right":
            self.activated.emit(self.selectionModel().currentIndex())
        elif direction == "left":
            libpaths.load("..")
        else:
            try:
                row = self.row()
            # Directory is empty
            except IndexError:
                raise cmdexc.CommandError("Directory is empty")
            if direction == "up":
                row -= count
            else:
                row += count
            self._select_row(row % self.model().rowCount())

    @keybindings.add("gg", "goto 1", mode="library")
    @keybindings.add("G", "goto -1", mode="library")
    @commands.argument("row", type=int)
    @commands.register(instance="library", mode="library", count=0)
    def goto(self, row, count):
        """Select row in library.

        Args:
            row: Number of the row to select of no count is given.
                -1 is the last row.
        """
        row = count if count else row  # Prefer count
        if row > 0:
            row -= 1  # Start indexing at 1
        row = (row) % (self.model().rowCount())
        self._select_row(row)

    def resizeEvent(self, event):
        """Resize columns on resize event."""
        width = self.width()
        self.setColumnWidth(0, 0.1 * width)
        self.setColumnWidth(1, 0.7 * width)
        self.setColumnWidth(2, 0.2 * width)
        super().resizeEvent(event)

    def current(self):
        """Return name of currently selected path."""
        try:
            return self.selectionModel().selectedIndexes()[1].data()
        except IndexError:
            return ""


class LibraryModel(QStandardItemModel):
    """Model used for the library.

    The model stores the rows.
    """

    def remove_all_rows(self):
        """Remove all rows from the model.

        This is implemented as a replacement for clear() which does not remove
        formatting.
        """
        self.removeRows(0, self.rowCount())


class LibraryDelegate(QStyledItemDelegate):
    """Delegate used for the library.

    The delegate draws the items.
    """

    def createEditor(self, *args):
        """Library is not editable by the user."""
        return None

    def paint(self, painter, option, index):
        """Override the QStyledItemDelegate paint function.

        Args:
            painter: QPainter * painter
            option: const QStyleOptionViewItem & option
            index: const QModelIndex & index
        """
        font = QFont()
        align = Qt.AlignLeft
        if index.column() == 0:
            font.setBold(True)
        elif index.column() == 1:
            pass
        else:
            align = Qt.AlignRight
        option.font = font
        option.displayAlignment = align
        super().paint(painter, option, index)
