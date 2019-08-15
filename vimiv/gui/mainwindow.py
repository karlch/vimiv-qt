# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QMainWindow which groups all the other widgets."""

from PyQt5.QtCore import QMargins
from PyQt5.QtWidgets import QWidget, QStackedLayout, QGridLayout

from vimiv import api, utils
from vimiv.completion import completer
from vimiv.config import configcommands

# Import all GUI widgets used to create the full main window
from . import statusbar
from .bar import Bar
from .commandline import CommandLine
from .completionwidget import CompletionView
from .image import ScrollableImage
from .keyhint_widget import KeyhintWidget
from .library import Library
from .manipulate import Manipulate, ManipulateImage
from .thumbnail import ThumbnailView
from .version_popup import VersionPopUp


class MainWindow(QWidget):
    """QMainWindow which groups all the other widgets.

    Attributes:
        _bar: bar.Bar object containing statusbar and command line.
        _overlays: List of overlay widgets.
        _stack: ImageThumbnailLayout as main layout widget.
    """

    @api.objreg.register
    def __init__(self):
        super().__init__()
        statusbar.init()
        commandline = CommandLine()

        self._bar = Bar(statusbar.statusbar, commandline)
        self._overlays = []

        grid = QGridLayout(self)
        grid.setSpacing(0)
        grid.setContentsMargins(QMargins(0, 0, 0, 0))

        self._stack = ImageThumbnailLayout()

        # Create widgets and add to layout
        lib = Library(self)
        grid.addLayout(self._stack, 0, 1, 1, 1)
        grid.addWidget(lib, 0, 0, 1, 1)
        manwidget = Manipulate(self)
        self._overlays.append(manwidget)
        self._overlays.append(ManipulateImage(self, manwidget))
        compwidget = CompletionView(self)
        self._overlays.append(compwidget)
        self._overlays.append(KeyhintWidget(self))
        grid.addWidget(self._bar, 1, 0, 1, 2)
        # Initialize completer and config commands
        completer.Completer(commandline, compwidget)
        configcommands.init()
        self._set_title()

        api.status.signals.update.connect(self._set_title)
        api.modes.COMMAND.entered.connect(self._update_overlay_geometry)
        api.modes.COMMAND.left.connect(self._update_overlay_geometry)
        api.settings.statusbar.show.changed.connect(self._update_overlay_geometry)

    @api.keybindings.register("f", "fullscreen", mode=api.modes.MANIPULATE)
    @api.keybindings.register("f", "fullscreen")
    @api.commands.register(mode=api.modes.MANIPULATE)
    @api.commands.register()
    def fullscreen(self):
        """Toggle fullscreen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    @api.commands.register()
    def version(self, copy: bool = False) -> None:
        """Show a pop-up with version information.

        **syntax:** ``:version [--copy]``

        optional arguments:
            * ``--copy``: Copy version information to clipboard instead.
        """
        if copy:
            VersionPopUp.copy_to_clipboard()
        else:
            VersionPopUp(parent=self)

    def resizeEvent(self, event):
        """Update resize event to resize overlays and library.

        Args:
            event: The QResizeEvent.
        """
        super().resizeEvent(event)
        self._update_overlay_geometry()
        api.objreg.get(Library).update_width()

    def show(self):
        """Update show to resize overlays."""
        super().show()
        self._update_overlay_geometry()

    def _update_overlay_geometry(self):
        """Update geometry of all overlay widgets according to current layout."""
        bottom = self.height()
        if self._bar.isVisible():
            bottom -= self._bar.height()
        for overlay in self._overlays:
            overlay.update_geometry(self.width(), bottom)

    def focusNextPrevChild(self, _next_child):
        """Override to do nothing as focusing is handled by modehandler."""
        return False

    @utils.slot
    def _set_title(self):
        """Update window title depending on mode and settings."""
        mode = api.modes.current().name
        try:  # Prefer mode specific setting
            title = api.settings.get_value("title.%s" % (mode))
        except KeyError:
            title = api.settings.get_value("title.fallback")
        self.setWindowTitle(api.status.evaluate(title))


def instance():
    return api.objreg.get(MainWindow)


class ImageThumbnailLayout(QStackedLayout):
    """QStackedLayout to toggle between image and thumbnail mode.

    Attributes:
        image: The image widget.
        thumbnail: The thumbnail widget.
    """

    def __init__(self):
        super().__init__()
        self.image = ScrollableImage()
        self.thumbnail = ThumbnailView()
        self.addWidget(self.image)
        self.addWidget(self.thumbnail)
        self.setCurrentWidget(self.image)

        api.modes.IMAGE.entered.connect(self._enter_image)
        api.modes.THUMBNAIL.entered.connect(self._enter_thumbnail)
        # This is required in addition to the setting when entering image mode as it is
        # possible to leave for the library
        api.modes.THUMBNAIL.left.connect(self._enter_image)

    def _enter_thumbnail(self):
        self.setCurrentWidget(self.thumbnail)

    def _enter_image(self):
        self.setCurrentWidget(self.image)
