# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""QMainWindow which groups all the other widgets.

Signals:
    resized: Emitted when the main window was resized.
"""

from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QGridLayout

from vimiv.commands import commands
from vimiv.config import styles, keybindings
from vimiv.gui import image, bar
from vimiv.utils import objreg


class MainWindow(QWidget):
    """QMainWindow which groups all the other widgets."""

    STYLESHEET = """
    QWidget {
        background-color: {statusbar.bg};
    }
    """

    @objreg.register("mainwindow")
    def __init__(self):
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setSpacing(0)
        self.grid.setContentsMargins(QMargins(0, 0, 0, 0))
        self.init_bar()
        self.init_image()
        styles.apply(self)

    def init_image(self):
        im = image.ScrollableImage()
        self.grid.addWidget(im, 0, 1, 1, 1)

    def init_bar(self):
        b = bar.Bar()
        self.grid.addWidget(b, 1, 0, 1, 2)

    @keybindings.add("f")
    @commands.register(instance="mainwindow")
    def fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
