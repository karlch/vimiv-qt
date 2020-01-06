# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*imtransform - transformations such as rotate and flip*."""

import weakref
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform

from vimiv import api
from vimiv.utils import log


_logger = log.module_logger(__name__)


class Scale:
    """Helper class to store the current scale of an image."""

    def __init__(self):
        self.x = self.y = 1

    @property
    def changed(self) -> bool:
        return self.x != 1 or self.y != 1

    def rescale(self, dx: float, dy: float):
        self.x *= dx
        self.y *= dy

    def reset(self):
        self.x = self.y = 1


class Transform:
    """Apply transformations to an image.

    Provides the :rotate and :flip commands and applies transformations to a
    given pixmap.

    Attributes:
        _handler: weak reference to ImageFileHandler used to retrieve/set updated files.
        _transform: QTransform object used to apply transformations.
        _rotation_angle: Currently applied rotation angle in degrees.
        _flip_horizontal: Flip the image horizontally.
        _flip_vertical: Flip the image vertically.
    """

    @api.objreg.register
    def __init__(self, handler):
        self._handler = weakref.ref(handler)
        self._transform = QTransform()
        self._rotation_angle = 0
        self._flip_horizontal = self._flip_vertical = False
        self._scale = Scale()

    @api.keybindings.register("<", "rotate --counter-clockwise", mode=api.modes.IMAGE)
    @api.keybindings.register(">", "rotate", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def rotate(self, counter_clockwise: bool = False, count: int = 1):
        """Rotate the image.

        **syntax:** ``:rotate [--counter-clockwise]``

        optional arguments:
            * ``--counter-clockwise``: Rotate counter clockwise.

        **count:** multiplier
        """
        self._ensure_editable()
        angle = 90 * count * -1 if counter_clockwise else 90 * count
        self._transform.rotate(angle)
        if self._apply_transformations():
            self._rotation_angle = (self._rotation_angle + angle) % 360

    @api.keybindings.register("_", "flip --vertical", mode=api.modes.IMAGE)
    @api.keybindings.register("|", "flip", mode=api.modes.IMAGE)
    @api.commands.register(mode=api.modes.IMAGE)
    def flip(self, vertical: bool = False):
        """Flip the image.

        **syntax:** ``:flip [--vertical]``

        optional arguments:
            * ``--vertical``: Flip image vertically instead of horizontally.
        """
        self._ensure_editable()
        # Vertical flip but image rotated by 90 degrees
        if vertical and self._rotation_angle % 180:
            self._transform.scale(-1, 1)
        # Standard vertical flip
        elif vertical:
            self._transform.scale(1, -1)
        # Horizontal flip but image rotated by 90 degrees
        elif self._rotation_angle % 180:
            self._transform.scale(1, -1)
        # Standard horizontal flip
        else:
            self._transform.scale(-1, 1)
        if self._apply_transformations():
            # Store changes
            if vertical:
                self._flip_vertical = not self._flip_vertical
            else:
                self._flip_horizontal = not self._flip_horizontal

    @api.commands.register(mode=api.modes.IMAGE)
    def resize(self, width: int, height: Optional[int]):
        """Resize the original image to a new size.

        **syntax:** ``:resize width [height]``

        positional arguments:
            * ``width``: Width in pixels to resize the image to.
            * ``height``: Height in pixels to resize the image to. If not given, the
              aspectratio is preserved.

        .. note:: This transforms the original image and writes to disk.
        """
        dx = width / self._handler().transformed.width()
        dy = dx if height is None else height / self._handler().transformed.height()
        self.rescale(dx, dy)

    @api.commands.register(mode=api.modes.IMAGE)
    def rescale(self, dx: float, dy: Optional[float]):
        """Rescale the original image to a new size.

        **syntax:** ``:rescale dx [dy]``

        positional arguments:
            * ``dx``: Factor in x direction to scale the image by.
            * ``dy``: Factor in y direction to scale the image by. If not given, the
              aspectratio is preserved.

        .. note:: This transforms the original image and writes to disk.
        """
        dy = dy if dy is not None else dx
        self._transform.scale(dx, dy)
        if self._apply_transformations():
            self._scale.rescale(dx, dy)
            _logger.debug("Updated scale to %.2fx%.2f", self._scale.x, self._scale.y)

    def _apply_transformations(self) -> bool:
        """Apply all transformations to the original pixmap.

        Returns:
            True if the application was successfull, False otherwise.
        """
        transformed = self._handler().original.transformed(
            self._transform, mode=Qt.SmoothTransformation
        )
        if transformed.isNull():
            log.error(
                "Error transforming image, ignoring transformation.\n"
                "Is the resulting image too large? Zero?."
            )
            return False
        self._handler().transformed = transformed
        return True

    def _ensure_editable(self):
        if not self._handler().editable:
            raise api.commands.CommandError("File format does not support transform")

    @property
    def changed(self):
        """True if transformations have been applied."""
        return (
            self._rotation_angle
            or self._flip_horizontal
            or self._flip_vertical
            or self._scale.changed
        )

    def reset(self):
        """Reset transformations."""
        self._transform.reset()
        self._rotation_angle = 0
        self._flip_horizontal = self._flip_vertical = False
        self._scale.reset()

    @api.commands.register(mode=api.modes.IMAGE)
    def reset_transformations(self):
        """Reset all performed transformations to default."""
        # We call reset and update the handler as reset is usually called by the handler
        # which updates the images itself
        self.reset()
        self._handler().transformed = self._handler().original
