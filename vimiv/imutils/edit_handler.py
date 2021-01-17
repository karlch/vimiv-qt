# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler class as man-in-the-middle between file handler and the edit classes."""

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QPixmap

from vimiv import api, utils
from vimiv.imutils import current_pixmap, imtransform


class EditHandler(QObject):
    """Man-in-the-middle between file handler and the various edit classes.

    Attributes:
        transform: Transform class for transformations such as rotate and flip.
        manipulate: Manipulate class for more complex changes such as brightness.

        _current_pixmap: Class to access and update the currently displayed pixmap.
        _manipulated: True if manipulations of the current image have been accepted.
    """

    def __init__(self):
        super().__init__()
        self._current_pixmap = current_pixmap.CurrentPixmap()
        self._manipulated = False

        self.transform = imtransform.Transform(self._current_pixmap)
        self.manipulate = None

        self.transform.transformed.connect(self._change_current)
        api.modes.MANIPULATE.first_entered.connect(self._init_manipulate)

    @property
    def changed(self):
        """True if the current image was edited in any way."""
        return self.transform.changed or self._manipulated

    @property
    def pixmap(self):
        """The currently displayed pixmap.

        Upon setting pixmaps of various attributes are updated accordingly.
        """
        return self._current_pixmap.pixmap

    @pixmap.setter
    def pixmap(self, pixmap):
        self._current_pixmap.pixmap = self.transform.original = pixmap

    def reset(self):
        self.transform.reset()
        self._manipulated = False

    def clear(self):
        self._current_pixmap.pixmap = QPixmap()

    @utils.slot
    def _change_current(self, pixmap: QPixmap):
        """Update the current pixmap emitting the pixmap_loaded signal reload-only."""
        self._current_pixmap.pixmap = pixmap
        reload_only = True
        api.signals.pixmap_loaded.emit(pixmap, reload_only)

    @utils.slot
    def _init_manipulate(self):
        """Initialize the Manipulator widget from the immanipulate module."""
        from vimiv.imutils import immanipulate

        self.manipulate = immanipulate.Manipulator(self._current_pixmap)
        self.manipulate.accepted.connect(self._on_manipulate_accepted)

    @utils.slot
    def _on_manipulate_accepted(self, pixmap: QPixmap):
        """Update pixmaps and store the status when manipulations were accepted."""
        self._change_current(pixmap)
        self._manipulated = True
        self.transform.original = pixmap
