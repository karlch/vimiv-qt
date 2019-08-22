# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Overlay widget to display image metadata."""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy

from vimiv import api, utils
from vimiv.imutils import exif
from vimiv.config import styles


_logger = utils.log.module_logger(__name__)


if exif.piexif is not None:

    class MetadataWidget(QLabel):
        """Overlay widget to display image metadata.

        The display of the widget can be toggled by command. It is filled with exif
        metadata information of the current image.


        Attributes:
            _mainwindow_bottom: y-coordinate of the bottom of the mainwindow.
            _mainwindow_width: width of the mainwindow.
            _path: Absolute path of the current image to load exif metadata of.
            _loaded: True if metadata has been loaded for the current image.
        """

        STYLESHEET = """
        QLabel {
            font: {statusbar.font};
            color: {statusbar.fg};
            background: {metadata.bg};
            padding: {metadata.padding};
            border-top-left-radius: {metadata.border_radius};
        }
        """

        @api.objreg.register
        def __init__(self, parent):
            super().__init__(parent=parent)
            styles.apply(self)

            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
            self.setTextFormat(Qt.RichText)

            self._mainwindow_bottom = 0
            self._mainwindow_width = 0
            self._path = ""
            self._loaded = False

            api.signals.new_image_opened.connect(self._on_image_opened)

            self.hide()

        @api.keybindings.register("i", "metadata", mode=api.modes.IMAGE)
        @api.commands.register(mode=api.modes.IMAGE)
        def metadata(self):
            """Toggle display of exif metadata of current image."""
            if self.isVisible():
                _logger.debug("Hiding widget")
                self.hide()
            else:
                _logger.debug("Showing widget")
                self._update_text()
                self.raise_()
                self.show()

        def update_geometry(self, window_width, window_bottom):
            """Adapt location when main window geometry changes."""
            self._mainwindow_width = window_width
            self._mainwindow_bottom = window_bottom
            self._update_geometry()

        def _update_geometry(self):
            """Update geometry according to current text content and window location."""
            self.adjustSize()
            y = self._mainwindow_bottom - self.height()
            self.setGeometry(
                self._mainwindow_width - self.width(), y, self.width(), self.height()
            )

        def _update_text(self):
            """Update the metadata text if the current image has not been loaded."""
            if self._loaded:
                return
            _logger.debug(
                "%s: reading exif of %s", self.__class__.__qualname__, self._path
            )
            text = ""
            for tag, content in exif.ExifInformation(self._path).items():
                text += (
                    "<tr>"
                    f"<td>{tag}</td>"
                    f"<td style='padding-left: 2ex'>{content}</td>"
                    "</tr>"
                )
            self.setText(f"<table>{text}</table>")
            self._update_geometry()
            self._loaded = True

        @utils.slot
        def _on_image_opened(self, path: str):
            """Load new image and update text if the widget is currently visible."""
            self._path = path
            self._loaded = False
            if self.isVisible():
                self._update_text()


else:  # No exif support
    MetadataWidget = None  # type: ignore
