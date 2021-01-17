# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Overlay widget to display image metadata."""

import itertools
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy

from vimiv import api, utils
from vimiv.imutils import exif
from vimiv.config import styles

_logger = utils.log.module_logger(__name__)


if exif.has_exif_support:

    class MetadataWidget(QLabel):
        """Overlay widget to display image metadata.

        The display of the widget can be toggled by command. It is filled with exif
        metadata information of the current image.


        Attributes:
            _mainwindow_bottom: y-coordinate of the bottom of the mainwindow.
            _mainwindow_width: width of the mainwindow.
            _path: Absolute path of the current image to load exif metadata of.
            _current_set: Holds a string of the currently selected keyset.
            _handler: ExifHandler for _path or None. Use the handler property to access.
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
            self._current_set = ""
            self._handler: Optional[exif.ExifHandler] = None

            api.signals.new_image_opened.connect(self._on_image_opened)
            api.settings.metadata.current_keyset.changed.connect(self._update_text)

            self.hide()

        @property
        def handler(self) -> exif.ExifHandler:
            """Return the ExifHandler for the current path."""
            if self._handler is None:
                self._handler = exif.ExifHandler(self._path)
            return self._handler

        @api.keybindings.register("i", "metadata", mode=api.modes.IMAGE)
        @api.commands.register(mode=api.modes.IMAGE)
        def metadata(self, count: Optional[int] = None):
            """Toggle display of exif metadata of current image.

            **count:** Select the key set to display instead.

            .. hint::
                3 default key sets are provided and mapped to the counts 1-3. To
                override them or add your own, extend the METADATA section in your
                configfile like this::

                    keys2 = Override,Second,Set
                    keys4 = New,Fourth,Set

                where the values must be a comma-separated list of valid metadata keys.
            """

            if count is not None:
                try:
                    _logger.debug("Switch keyset")
                    new_keyset = api.settings.metadata.keysets[count]
                    api.settings.metadata.current_keyset.value = new_keyset
                    if not self.isVisible():
                        _logger.debug("Showing widget")
                        self.raise_()
                        self.show()
                except KeyError:
                    raise api.commands.CommandError(f"Invalid key set option {count}")
            elif self.isVisible():
                _logger.debug("Hiding widget")
                self.hide()
            else:
                _logger.debug("Showing widget")
                self._update_text()
                self.raise_()
                self.show()

        @api.commands.register(mode=api.modes.IMAGE)
        def metadata_list_keys(self, n_cols: int = 3, to_term: bool = False):
            """Display a list of all valid metadata keys for the current image.

            **syntax:** ``:metadata-list-keys [--n-cols=NUMBER] [--to-term]``

            optional arguments:
                * ``--n-cols``: Number of columns used to display the keys.
                * ``--to-term``: Print the keys to the terminal instead.
            """

            keys = sorted(set(self.handler.get_keys()))
            if to_term:
                print(*keys, sep="\n")
            elif n_cols < 1:
                raise api.commands.CommandError("Number of columns must be positive")
            else:
                columns = list(utils.split(keys, n_cols))
                table = utils.format_html_table(
                    itertools.zip_longest(*columns, fillvalue="")
                )
                self.setText(table)
                self._update_geometry()
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
            if self._current_set == api.settings.metadata.current_keyset.value:
                return
            _logger.debug(
                "%s: reading exif of %s", self.__class__.__qualname__, self._path
            )
            keys = [
                e.strip() for e in api.settings.metadata.current_keyset.value.split(",")
            ]
            _logger.debug(f"Read metadata.current_keys {keys}")
            formatted_exif = self.handler.get_formatted_exif(keys)
            if formatted_exif:
                self.setText(utils.format_html_table(formatted_exif.values()))
            else:
                self.setText("No matching metadata found")
            self._update_geometry()
            self._current_set = api.settings.metadata.current_keyset.value

        @utils.slot
        def _on_image_opened(self, path: str):
            """Load new image and update text if the widget is currently visible."""
            self._path = path
            self._current_set = ""
            self._handler = None
            if self.isVisible():
                self._update_text()


else:  # No exif support  # pragma: no cover  # Covered in another CI
    MetadataWidget = None  # type: ignore
