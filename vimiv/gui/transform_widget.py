# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Base class for widgets which provide a gui for more complex transformations."""

import abc
import functools
from contextlib import suppress

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

from vimiv.imutils import imtransform

# See https://github.com/PyCQA/pylint/issues/3202
from vimiv import api, utils  # pylint: disable=unused-import

from .eventhandler import keyevent_to_sequence


class TransformWidget(QWidget, metaclass=utils.AbstractQObjectMeta):
    """Base class for widgets which provide a gui for more complex transformations.

    The child class must implement update_geometry to adapt to a resized image and
    should provide additional keybindings which implement the actual transformation.
    """

    def __init__(self, image, **bindings):
        super().__init__(parent=image)
        self.setObjectName(self.__class__.__qualname__)
        self.setWindowFlags(Qt.SubWindow)
        self.setFocus()

        self.bindings = {
            ("<escape>",): self.leave,
            ("<return>",): functools.partial(self.leave, accept=True),
            **bindings,
        }
        self.transform = imtransform.Transform.instance
        self.previous_matrix = self.transform.matrix

        image.resized.connect(self.update_geometry)
        self.update_geometry()
        self.show()

    @abc.abstractmethod
    def update_geometry(self):
        """Update geometry of the widget."""

    def leave(self, accept: bool = False):
        """Leave the transform widget for image mode.

        Args:
            accept: If True, keep the straightening as transformation.
        """
        if not accept:
            self.reset_transformations()
            self.transform.apply()
        self.parent().setFocus()  # type: ignore

    def reset_transformations(self):
        self.transform.setMatrix(*self.previous_matrix)

    def keyPressEvent(self, event):
        """Run binding from bindings dictionary."""
        with suppress(ValueError, KeyError):
            keysequence = keyevent_to_sequence(event)
            binding = self.bindings[keysequence]
            api.status.clear("straighten binding")
            binding()
            api.status.update("straighten binding")

    def focusOutEvent(self, event):
        """Delete the widget when focusing out."""
        self.deleteLater()
        super().focusOutEvent(event)
