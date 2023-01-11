# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to be used as custom types for vimiv commands..

Example for scroll direction:
    def scroll(self, direction: argtypes.Direction):
        ...
"""

import re
import contextlib
import enum

from PyQt5.QtCore import QSize


class Direction(enum.Enum):
    """Valid arguments for directional commands."""

    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"


class DirectionWithPage(enum.Enum):
    """Valid arguments for directional commands that support page scrolling."""

    Left = Direction.Left.value
    Right = Direction.Right.value
    Up = Direction.Up.value
    Down = Direction.Down.value
    PageUp = "page-up"
    PageDown = "page-down"
    HalfPageUp = "half-page-up"
    HalfPageDown = "half-page-down"

    @property
    def is_page_step(self):
        return self in (self.PageUp, self.PageDown, self.HalfPageUp, self.HalfPageDown)

    @property
    def is_half_page_step(self):
        return self in (self.HalfPageUp, self.HalfPageDown)

    @property
    def is_reverse(self):
        return self in (self.Left, self.Up, self.PageUp, self.HalfPageUp)


class Zoom(enum.Enum):
    """Valid arguments for zooming."""

    In = "in"
    Out = "out"


class ImageScale(str, enum.Enum):
    """Valid arguments for image scaling."""

    Overzoom = "overzoom"
    Fit = "fit"
    FitWidth = "fit-width"
    FitHeight = "fit-height"


class ImageScaleFloat:
    """Valid arguments for image scaling including float and ImageScale."""

    def __new__(cls, value):
        with contextlib.suppress(ValueError):
            return float(value)
        return ImageScale(value)


class HistoryDirection(enum.Enum):
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

    Attributes:
        keep: True if the aspectratio of the original image should be kept.
    """

    SEPARATORS = ":,-_"

    def __init__(self, aspectratio: str):
        if aspectratio.lower() == "keep":
            self.keep = True
            super().__init__()
        else:
            self.keep = False
            split_re = "|".join(self.SEPARATORS)
            try:
                width, height = tuple(re.split(split_re, aspectratio))
                super().__init__(int(width), int(height))
            except ValueError:
                raise ValueError(
                    f"'Invalid aspectratio '{aspectratio}'. Use width:height, e.g. 4:3"
                ) from None
