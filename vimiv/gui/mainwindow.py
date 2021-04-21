# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""QMainWindow which groups all the other widgets."""

from typing import List

from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout

from vimiv import api, utils
from vimiv.utils import migration

# Import all GUI widgets used to create the full main window
from vimiv.gui.commandwidget import CommandWidget
from vimiv.gui.image import ScrollableImage
from vimiv.gui.keyhintwidget import KeyhintWidget
from vimiv.gui.library import Library
from vimiv.gui.thumbnail import ThumbnailView
from vimiv.gui.message import Message
from vimiv.gui.metadatawidget import MetadataWidget
from vimiv.gui.statusbar import StatusBar


class MainWindow(QWidget):
    """QMainWindow which groups all the other widgets.

    Attributes:
        _library: Library object at the left of the grid.
        _overlays: List of overlay widgets.
        _statusbar: Statusbar object displayed at the bottom.
    """

    @api.objreg.register
    def __init__(self):
        super().__init__()
        self._overlays: List[QWidget] = []
        # Create main widgets and add them to the grid layout
        self._statusbar = StatusBar()
        grid = QGridLayout(self)
        grid.setSpacing(0)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.addWidget(ImageThumbnailStack(), 0, 1, 1, 1)
        self._library = Library(self)
        grid.addWidget(self._library, 0, 0, 1, 1)
        grid.addWidget(self._statusbar, 1, 0, 1, 2)
        # Add overlay widgets
        self._overlays.append(KeyhintWidget(self))
        self._overlays.append(Message(self))
        self._overlays.append(CommandWidget(self))
        if MetadataWidget is not None:  # Not defined if there is no metadata support
            self._overlays.append(MetadataWidget(self))
        # Connect signals
        api.status.signals.update.connect(self._set_title)
        api.settings.statusbar.show.changed.connect(self._update_overlay_geometry)
        api.modes.MANIPULATE.first_entered.connect(self._init_manipulate)
        api.prompt.question_asked.connect(self._run_prompt)

    @utils.slot
    def _init_manipulate(self):
        """Create UI widgets related to manipulate mode."""
        from vimiv.gui.manipulate import Manipulate

        manipulate_widget = Manipulate(self)
        self.add_overlay(manipulate_widget)

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
        from vimiv.gui.version_popup import VersionPopUp

        if copy:
            VersionPopUp.copy_to_clipboard()
        else:
            VersionPopUp(parent=self)

    @api.commands.register(mode=api.modes.MANIPULATE)
    @api.commands.register()
    def keybindings(self, columns: int = 2):
        """Show a pop-up with keybindings information.

        **syntax:** ``:keybindings [--columns=N]``

        optional arguments:
            * ``--columns``: Number of columns to split the bindings in.
        """
        from vimiv.gui.keybindings_popup import KeybindingsPopUp

        KeybindingsPopUp(columns, parent=self)

    @api.commands.register()
    def welcome_to_qt(self):
        """Show a pop-up with a welcome message for users coming from gtk."""
        migration.WelcomePopUp(parent=self)

    def resizeEvent(self, event):
        """Update resize event to resize overlays and library.

        Args:
            event: The QResizeEvent.
        """
        super().resizeEvent(event)
        self._update_overlay_geometry()
        self._library.update_width()

    def show(self):
        """Update show to resize overlays."""
        super().show()
        self._update_overlay_geometry()

    @property
    def bottom(self):
        """Bottom of the main window respecting the status bar height."""
        if self._statusbar.isVisible():
            return self.height() - self._statusbar.height()
        return self.height()

    def add_overlay(self, widget, resize=True):
        """Add a new overlay widget to the main window and update its geometry."""
        self._overlays.append(widget)
        if resize:
            widget.update_geometry(self.width(), self.bottom)

    def _update_overlay_geometry(self):
        """Update geometry of all overlay widgets according to current layout."""
        bottom = self.bottom
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
            title = api.settings.get_value(f"title.{mode}")
        except KeyError:
            title = api.settings.get_value("title.fallback")
        self.setWindowTitle(api.status.evaluate(title))

    @utils.slot
    def _run_prompt(self, question: api.prompt.Question) -> None:
        """Display a UI blocking prompt when a question was asked."""
        from vimiv.gui.prompt import Prompt

        prompt = Prompt(question, parent=self)
        prompt.update_geometry(self.width(), self.bottom)
        prompt.run()


class ImageThumbnailStack(QStackedWidget):
    """QStackedWidget to toggle between image and thumbnail mode.

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

        api.modes.IMAGE.entered.connect(self._enter_image)
        api.modes.THUMBNAIL.entered.connect(self._enter_thumbnail)
        # This is required in addition to the setting when entering image mode as it is
        # possible to close thumbnail mode and enter the library
        api.modes.THUMBNAIL.closed.connect(self._enter_image)

    @utils.slot
    def _enter_thumbnail(self):
        self.setCurrentWidget(self.thumbnail)

    @utils.slot
    def _enter_image(self):
        self.setCurrentWidget(self.image)
