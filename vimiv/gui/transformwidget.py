# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Base class for widgets which provide a gui for more complex transformations."""

import contextlib
import functools
from typing import cast

from vimiv.qt.core import Qt, QRect
from vimiv.qt.widgets import QWidget

from vimiv.imutils import imtransform

from vimiv import api
from vimiv.gui import eventhandler
from .image import ScrollableImage


class TransformWidget(QWidget):
    """Base class for widgets which provide a gui for more complex transformations.

    The child class must implement update_geometry to adapt to a resized image and
    should provide additional keybindings which implement the actual transformation.

    Attributes:
        bindings: Dictionary mapping keybindings to the corresponding methods.
        transform: Transform instance to perform the actual transformations.
        previous_matrix: Transformation matrix before starting changes here.
    """

    def __init__(self, image):
        super().__init__(parent=image)
        self.setObjectName(self.__class__.__qualname__)
        self.setWindowFlags(Qt.WindowType.SubWindow)
        self.setFocus()

        self.bindings = {
            ("<escape>",): self.leave,
            ("<return>",): functools.partial(self.leave, accept=True),
        }
        self.transform = imtransform.Transform.instance
        self.previous_matrix = self.transform.matrix

        image.transformation_module = self.status_info

        image.resized.connect(self.update_geometry)

    @property
    def image(self) -> ScrollableImage:
        return cast(ScrollableImage, self.parent())

    def update_geometry(self):
        """Update geometry of the widget."""
        raise NotImplementedError("Must be implemented by the actual transformation")

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
        self.image.transformation_module = None
        self.image.setFocus()
        self.deleteLater()
        api.status.update("transform widget left")

    def reset_transformations(self):
        self.transform.setMatrix(*self.previous_matrix)

    @property
    def image_rect(self) -> QRect:
        """Rectangle occupied by the image within the parent widget."""
        return self.image.mapFromScene(self.image.sceneRect()).boundingRect()

    def keyPressEvent(self, event):
        """Run binding from bindings dictionary."""
        with contextlib.suppress(ValueError, KeyError):
            keysequence = eventhandler.keyevent_to_sequence(event)
            binding = self.bindings[keysequence]
            api.status.clear("transform binding")
            binding()
            api.status.update("transform binding")

    def focusOutEvent(self, event):
        """Leave the widget when the user focuses another widget."""
        ignored_reasons = (
            Qt.FocusReason.ActiveWindowFocusReason,  # Unfocused the whole window
            Qt.FocusReason.OtherFocusReason,  # Unfocused explicitly during leave
        )
        if event.reason() not in ignored_reasons:
            self.leave(accept=False)
