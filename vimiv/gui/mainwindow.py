# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""QMainWindow which groups all the other widgets.

Signals:
    resized: Emitted when the main window was resized.
"""

from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QGridLayout, QStackedLayout

from vimiv.commands import commands
from vimiv.completion import completer
from vimiv.config import styles, keybindings, configcommands
from vimiv.gui import image, bar, library, completionwidget, thumbnail
from vimiv.utils import objreg


class MainWindow(QWidget):
    """QMainWindow which groups all the other widgets.

    Attributes:
        _overlays: List of overlay widgets.
    """

    STYLESHEET = """
    QWidget {
        background-color: {statusbar.bg};
    }

    Attributes:
        bar: bar.Bar object containing statusbar and command line.
        stack: Stack containing thumbnail and image.
    """

    @objreg.register("mainwindow")
    def __init__(self):
        super().__init__()
        self._overlays = []
        # Create layout
        self.grid = QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(QMargins(0, 0, 0, 0))
        self.stack = QStackedLayout()
        self.bar = bar.Bar()
        # Create widgets and add to layout
        im = image.ScrollableImage(self.stack)
        thumb = thumbnail.ThumbnailView(self.stack)
        self.stack.addWidget(im)
        self.stack.addWidget(thumb)
        self.stack.setCurrentWidget(im)
        lib = library.Library()
        self.grid.addLayout(self.stack, 0, 1, 1, 1)
        self.grid.addWidget(lib, 0, 0, 1, 1)
        compwidget = completionwidget.CompletionView(self)
        self._overlays.append(compwidget)
        self.grid.addWidget(self.bar, 1, 0, 1, 2)
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
        """Update resize event to resize overlays.

        Args:
            event: The QResizeEvent.
        """
        super().resizeEvent(event)
        bottom = self.height()
        if self.bar.isVisible():
            bottom -= self.bar.height()
        for overlay in self._overlays:
            overlay.update_geometry(self.width(), bottom)

    def focusNextPrevChild(self, next_child):
        """Override to do nothing as focusing is handled by modehandler."""
        return False
