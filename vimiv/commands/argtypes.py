# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to be used as custom types for vimiv commands..

Example for scroll direction:
    def scroll(self, direction: argtypes.Direction):
        ...
"""

import re
from contextlib import suppress
from enum import Enum

from PyQt5.QtCore import QSize


class Direction(Enum):
    """Valid arguments for directional commands."""

    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"


class Zoom(Enum):
    """Valid arguments for zooming."""

    In = "in"
    Out = "out"


class ImageScale(str, Enum):
    """Valid arguments for image scaling."""

    Overzoom = "overzoom"
    Fit = "fit"
    FitWidth = "fit-width"
    FitHeight = "fit-height"


class ImageScaleFloat:
    """Valid arguments for image scaling including float and ImageScale."""

    def __new__(cls, value):
        with suppress(ValueError):
            return float(value)
        return ImageScale(value)


class HistoryDirection(Enum):
    """Valid arguments for the jumping through history."""

    Next = "next"
    Prev = "prev"


class AspectRatio(QSize):
    """Aspectratio defined as QSize with width and height from a valid string.

    Valid definitions are strings with two integer values representing width and height
    separated by one of the characters in SEPARATORS.

    Examples:
        4:3
        16,9
        5_4
    """

    SEPARATORS = ":,-_"

    def __init__(self, aspectratio: str):
        split_re = "|".join(self.SEPARATORS)
        try:
            width, height = tuple(re.split(split_re, aspectratio))
            super().__init__(int(width), int(height))
        except ValueError:
            raise ValueError(
                f"'Invalid aspectratio '{aspectratio}'. Use width:height, e.g. 4:3"
            ) from None
