# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Library widget with model and delegate."""

import os

from PyQt5.QtCore import QItemSelectionModel, Qt
from PyQt5.QtWidgets import QStyledItemDelegate, QSizePolicy
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont

from vimiv import app
from vimiv.commands import commands, argtypes
from vimiv.config import styles, keybindings, settings
from vimiv.gui import widgets
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
        border: 0px;
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
        libpaths.signals.loaded.connect(self._on_paths_loaded)

        styles.apply(self)

    def _on_activated(self, index):
        """Open path correctly on activate.

        If the path activated is an image, it is opened in image mode. If it is
        a directory, the library is loaded for this directory.

        Args:
            index: The QModelIndex activated.
        """
        path_index = self.selectionModel().selectedIndexes()[1]
        path = path_index.data()
        app.open_paths([path], select_mode=False)  # We select mode later
        if path == self._last_selected:
            modehandler.enter("image")
            self.hide()
            self._last_selected = ""
        else:
            self._last_selected = path

    def _on_paths_loaded(self, images, directories):
        """Fill library with paths when they were loaded.

        Args:
            images: List of images.
            directories: List of directories.
        """
        self.model().remove_all_rows()
        self._add_directories(directories)
        self._add_images(images)
        self._select_row(0)

    def _add_directories(self, directories):
        """Add directories to the library.

        Args:
            directories: List of directories to add.
        """
        for directory in directories:
            index = str(self.model().rowCount() + 1)
            name = os.path.basename(directory) + "/"
            self._add_row(index, name, "0")

    def _add_images(self, images):
        """Add images to the library.

        Args:
            images: List of images to add.
        """
        for image in images:
            index = str(self.model().rowCount() + 1)
            name = os.path.basename(image)
            self._add_row(index, name, "0")

    def _add_row(self, index, name, size):
        """Add one row to the library.

        Args:
            index: String representation of the row number.
            name: Name of the path.
            size: Size of the path.
        """
        row = [QStandardItem(elem) for elem in [index, name, size]]
        self.model().appendRow(row)

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
            row = self.row()
            if direction == "up":
                row -= count
            else:
                row += count
            self._select_row(row % self.model().rowCount())

    @keybindings.add("g", "goto 1")
    @keybindings.add("G", "goto -1")
    @commands.argument("row", type=int)
    @commands.register(instance="library", mode="library", count=0)
    def goto(self, row, count):
        """Command to select a specific row in the library.

        Args:
            row: Number of the row to select of no count is given.
                -1 is the last row.
        """
        row = count if count else row  # Prefer count
        if row > 0:
            row -= 1  # Start indexing at 1
        row = (row) % (self.model().rowCount())
        self._select_row(row)

    def toggle(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()

    def _select_row(self, row):
        """Select a specific row in the library.

        Args:
            row: Number of the row to select.
        """
        index = self.model().index(row, 0)
        self._select_index(index)

    def _select_index(self, index):
        """Select a specific index in the library.

        Args:
            index: QModelIndex to select.
        """
        selmod = QItemSelectionModel.Rows | QItemSelectionModel.ClearAndSelect
        self.selectionModel().setCurrentIndex(index, selmod)

    def row(self):
        """Return the currently selected row."""
        selected_indexes = self.selectionModel().selectedIndexes()  # 3 columns
        return selected_indexes[0].row()

    def resizeEvent(self, event):
        """Resize columns on resize event."""
        width = self.width()
        self.setColumnWidth(0, 0.1 * width)
        self.setColumnWidth(1, 0.7 * width)
        self.setColumnWidth(2, 0.2 * width)
        super().resizeEvent(event)


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
