# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Perform simple transformations like rotate and flip."""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTransform

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.imutils import imsignals, imloader
from vimiv.modes import Modes
from vimiv.utils import objreg


class Transform():
    """Apply transformations to an image.

    Provides the :rotate and :flip commands and applies transformations to a
    given pixmap.

    Attributes:
        _transform: QTransform object used to apply transformations.
        _rotation_angle: Currently applied rotation angle in degrees.
        _flip_horizontal: Flip the image horizontally.
        _flip_vertical: Flip the image vertically.
    """

    @objreg.register
    def __init__(self):
        self._transform = QTransform()
        self._rotation_angle = 0
        self._flip_horizontal = self._flip_vertical = False

    @keybindings.add("<", "rotate --counter-clockwise", mode=Modes.IMAGE)
    @keybindings.add(">", "rotate", mode=Modes.IMAGE)
    @commands.argument("counter-clockwise", optional=True, action="store_true")
    @commands.register(mode=Modes.IMAGE, count=1)
    def rotate(self, counter_clockwise, count):
        """Rotate the image.

        **syntax:** ``:rotate [--counter-clockwise]``

        optional arguments:
            * ``--counter_clockwise``: Rotate counter clockwise.

        **count:** multiplier
        """
        angle = 90 * count * -1 if counter_clockwise else 90 * count
        self._rotation_angle += angle
        self._transform.rotate(angle)
        pixmap = self.transform_pixmap(imloader.current())
        imsignals.imsignals.pixmap_updated.emit(pixmap)

    @keybindings.add("_", "flip --vertical", mode=Modes.IMAGE)
    @keybindings.add("|", "flip", mode=Modes.IMAGE)
    @commands.argument("vertical", optional=True, action="store_true")
    @commands.register(mode=Modes.IMAGE)
    def flip(self, vertical):
        """Flip the image.

        **syntax:** ``:flip [--vertical]``

        optional arguments:
            * ``--vertical``: Flip image vertically instead of horizontally.
        """
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
        pixmap = self.transform_pixmap(imloader.current())
        # Store changes
        if vertical:
            self._flip_vertical = not self._flip_vertical
        else:
            self._flip_horizontal = not self._flip_horizontal
        imsignals.imsignals.pixmap_updated.emit(pixmap)

    def transform_pixmap(self, pm):
        """Apply all transformations to the given pixmap."""
        return pm.transformed(self._transform, mode=Qt.SmoothTransformation)

    def changed(self):
        """Return True if transformations have been applied."""
        if self._rotation_angle or self._flip_horizontal \
                or self._flip_vertical:
            return True
        return False

    def reset(self):
        """Reset transformations."""
        self._transform.reset()
        self._rotation_angle = 0
        self._flip_horizontal = self._flip_vertical = False
