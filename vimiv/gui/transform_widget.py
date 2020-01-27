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

    Attributes:
        bindings: Dictionary mapping keybindings to the corresponding methods.
        transform: Transform instance to perform the actual transformations.
        previous_matrix: Transformation matrix before starting changes here.
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

        image.transformation_module = self.status_info

        image.resized.connect(self.update_geometry)
        self.update_geometry()
        self.show()

    @abc.abstractmethod
    def update_geometry(self):
        """Update geometry of the widget."""

    def status_info(self) -> str:
        """Can be overridden by the child to display information in the status bar."""
        return ""

    def leave(self, accept: bool = False):
        """Leave the transform widget for image mode.

        Args:
            accept: If True, keep the straightening as transformation.
        """
        if not accept:
            self.reset_transformations()
            self.transform.apply()
        self.parent().transformation_module = None  # type: ignore
        self.parent().setFocus()  # type: ignore
        self.deleteLater()
        api.status.update("transform widget left")

    def reset_transformations(self):
        self.transform.setMatrix(*self.previous_matrix)

    def keyPressEvent(self, event):
        """Run binding from bindings dictionary."""
        with suppress(ValueError, KeyError):
            keysequence = keyevent_to_sequence(event)
            binding = self.bindings[keysequence]
            api.status.clear("transform binding")
            binding()
            api.status.update("transform binding")

    def focusOutEvent(self, event):
        """Leave the widget when the user focuses another widget."""
        ignored_reasons = (
            Qt.ActiveWindowFocusReason,  # Unfocused the whole window
            Qt.OtherFocusReason,  # Unfocused explicitly during leave
        )
        if event.reason() not in ignored_reasons:
            self.leave(accept=False)
