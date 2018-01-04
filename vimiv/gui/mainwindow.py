# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QMainWindow which groups all the other widgets."""

from PyQt5.QtWidgets import QWidget, QStackedLayout

from vimiv.commands import commands
from vimiv.completion import completer
from vimiv.config import styles, keybindings, configcommands
from vimiv.gui import image, bar, library, completionwidget, thumbnail, widgets
from vimiv.utils import objreg


class MainWindow(QWidget):
    """QMainWindow which groups all the other widgets.

    Attributes:
        bar: bar.Bar object containing statusbar and command line.

        _overlays: List of overlay widgets.
    """

    STYLESHEET = """
    QWidget {
        background-color: {statusbar.bg};
    }
    """

    @objreg.register("mainwindow")
    def __init__(self):
        super().__init__()
        self.bar = bar.Bar()
        self._overlays = []

        grid = widgets.SimpleGrid(self)
        stack = QStackedLayout()

        # Create widgets and add to layout
        im = image.ScrollableImage(stack)
        thumb = thumbnail.ThumbnailView(stack)
        stack.addWidget(im)
        stack.addWidget(thumb)
        stack.setCurrentWidget(im)
        lib = library.Library(self)
        grid.addLayout(stack, 0, 1, 1, 1)
        grid.addWidget(lib, 0, 0, 1, 1)
        compwidget = completionwidget.CompletionView(self)
        self._overlays.append(compwidget)
        grid.addWidget(self.bar, 1, 0, 1, 2)
        # Initialize completer and config commands
        completer.Completer(self.bar.commandline, compwidget)
        configcommands.init()

        styles.apply(self)

    @keybindings.add("f", "fullscreen")
    @commands.register(instance="mainwindow")
    def fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def resizeEvent(self, event):
        """Update resize event to resize overlays and library.

        Args:
            event: The QResizeEvent.
        """
        super().resizeEvent(event)
        bottom = self.height()
        if self.bar.isVisible():
            bottom -= self.bar.height()
        for overlay in self._overlays:
            overlay.update_geometry(self.width(), bottom)
        lib = objreg.get("library")
        lib.update_width()

    def focusNextPrevChild(self, next_child):
        """Override to do nothing as focusing is handled by modehandler."""
        return False
