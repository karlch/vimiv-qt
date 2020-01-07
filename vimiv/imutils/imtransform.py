# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*imtransform - transformations such as rotate and flip*."""

import functools
import math
import weakref
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform

from vimiv import api
from vimiv.utils import log


_logger = log.module_logger(__name__)


def register_transform_command(**kwargs):
    """Wrap commands.register to ensure image is editable and apply transformations."""

    def decorator(func):
        @functools.wraps(func)
        def inner(self, *args, **kwargs):
            # Only used to wrap methods of transform
            # pylint: disable=protected-access
            self._ensure_editable()
            func(self, *args, **kwargs)
            self._apply_transformations()

        return api.commands.register(mode=api.modes.IMAGE, **kwargs)(inner)

    return decorator


class Transform(QTransform):
    """Apply transformations to an image.

    Provides the commands related to transformation such as rotate and flip and is used
    to apply these transformations to the pixmap given by the handler.

    Attributes:
        _handler: weak reference to ImageFileHandler used to retrieve/set updated files.
    """

    @api.objreg.register
    def __init__(self, handler):
        super().__init__()
        self._handler = weakref.ref(handler)

    @property
    def angle(self) -> int:
        """Current rotation angle in degrees."""
        x, y = self.map(0, 1)
        return int(math.atan2(x, y) / math.pi * 180)

    @api.keybindings.register("<", "rotate --counter-clockwise", mode=api.modes.IMAGE)
    @api.keybindings.register(">", "rotate", mode=api.modes.IMAGE)
    @register_transform_command(name="rotate")
    def rotate_command(self, counter_clockwise: bool = False, count: int = 1):
        """Rotate the image.

        **syntax:** ``:rotate [--counter-clockwise]``

        optional arguments:
            * ``--counter-clockwise``: Rotate counter clockwise.

        **count:** multiplier
        """
        angle = 90 * count
        self.rotate(-angle if counter_clockwise else angle)

    @api.keybindings.register("_", "flip --vertical", mode=api.modes.IMAGE)
    @api.keybindings.register("|", "flip", mode=api.modes.IMAGE)
    @register_transform_command()
    def flip(self, vertical: bool = False):
        """Flip the image.

        **syntax:** ``:flip [--vertical]``

        optional arguments:
            * ``--vertical``: Flip image vertically instead of horizontally.
        """
        # Change direction if image is rotated by 90/270 degrees
        if self.angle % 180:
            vertical = not vertical
        if vertical:
            self.scale(1, -1)
        else:
            self.scale(-1, 1)

    @register_transform_command()
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
        self.scale(dx, dy)

    @register_transform_command()
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
        self.scale(dx, dy)

    def _apply_transformations(self):
        """Apply all transformations to the original pixmap."""
        transformed = self._handler().original.transformed(
            self, mode=Qt.SmoothTransformation
        )
        if transformed.isNull():
            raise api.commands.CommandError(
                "Error transforming image, ignoring transformation.\n"
                "Is the resulting image too large? Zero?."
            )
        self._handler().transformed = transformed

    def _ensure_editable(self):
        if not self._handler().editable:
            raise api.commands.CommandError("File format does not support transform")

    @property
    def changed(self):
        """True if transformations have been applied."""
        return not self.isIdentity()

    @api.commands.register(mode=api.modes.IMAGE)
    def reset_transformations(self):
        """Reset all performed transformations to default."""
        # We call reset and update the handler as reset is usually called by the handler
        # which updates the images itself
        self.reset()
        self._handler().transformed = self._handler().original
