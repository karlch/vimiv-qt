# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""*imtransform - transformations such as rotate and flip*."""

import functools
import math
import weakref
from typing import Optional

from PyQt5.QtCore import Qt, QRect, QSize
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
            self.apply()

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
    def angle(self) -> float:
        """Current rotation angle in degrees."""
        x, y = self.map(1.0, 0.0)
        return (math.atan2(y, x) / math.pi * 180) % 360

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

    def apply(self):
        """Apply all transformations to the original pixmap."""
        original = self._handler().original
        self._apply(original.transformed(self, mode=Qt.SmoothTransformation))

    def straighten(self, *, angle: int, original_size: QSize):
        """Straighten the original image.

        This rotates the image by the total angle and crops the valid, axis-aligned
        rectangle from the rotated image.

        Args:
            angle: Rotation angle to straighten the original image by.
            original_size: Size of the original unstraightened image.
        """
        original = self._handler().original
        self.rotate(angle)
        transformed = original.transformed(self, mode=Qt.SmoothTransformation)
        rect = self.largest_rect_in_rotated(
            original=original_size, rotated=transformed.size(), angle=angle
        )
        self._apply(transformed.copy(rect))

    def _apply(self, transformed):
        """Check the transformed pixmap for validity and apply it to the handler."""
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

    @property
    def matrix(self):
        """Tuple of matrix elements defining the current transformation matrix."""
        # fmt: off
        return (
            self.m11(), self.m12(), self.m13(),
            self.m21(), self.m22(), self.m23(),
            self.m31(), self.m32(), self.m33(),
        )
        # fmt: on

    @property
    def size(self) -> QSize:
        """Size of the transformed image."""
        return self._handler().transformed.size()

    @api.commands.register(mode=api.modes.IMAGE)
    def undo_transformations(self):
        """Undo any transformation applied to the current image."""
        self.reset()
        self._handler().transformed = self._handler().original

    @classmethod
    def largest_rect_in_rotated(
        cls, *, original: QSize, rotated: QSize, angle: float
    ) -> QRect:
        """Return largest possible axis-aligned rectangle in rotated rectangle.

        See https://stackoverflow.com/a/16778797 for the implementation details.

        Args:
            original: Size of the original (unrotated) rectangle.
            rotated: Size of the rotated and padded rectangle (larger than original).
            angle: Rotation angle in degrees.
        Returns:
            Rectangle with the coordinates and size within the rotated rectangle.
        """
        # Not beautiful, but also not much nicer if we refactor this into multiple
        # functions
        # pylint: disable=too-many-locals
        rad = angle / 180 * math.pi
        is_portrait = original.height() > original.width()
        short = original.width() if is_portrait else original.height()
        long = original.height() if is_portrait else original.width()
        sin_a = abs(math.sin(rad))
        cos_a = abs(math.cos(rad))

        if short <= 2.0 * sin_a * cos_a * long or abs(sin_a - cos_a) < 1e-10:
            s = 0.5 * short
            wr, hr = (s / cos_a, s / sin_a) if is_portrait else (s / sin_a, s / cos_a)
        else:
            cos_2a = cos_a ** 2 - sin_a ** 2
            wr = (original.width() * cos_a - original.height() * sin_a) / cos_2a
            hr = (original.height() * cos_a - original.width() * sin_a) / cos_2a

        x = (rotated.width() - wr) // 2
        y = (rotated.height() - hr) // 2

        return QRect(int(x), int(y), int(wr), int(hr))
