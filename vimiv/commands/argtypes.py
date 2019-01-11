# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to be used as custom types for vimiv commands..

Example for scroll direction:
    def scroll(self, direction: argtypes.Direction):
        ...
"""

from enum import Enum

from vimiv.utils import ignore


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
        with ignore(ValueError):
            return float(value)
        return ImageScale(value)


class HistoryDirection(Enum):
    """Valid arguments for the jumping through history."""

    Next = "next"
    Prev = "prev"


class ManipulateLevel(int):
    """Valid integer for manipulation (any integer between -127 and 127)."""

    def __new__(cls, value):
        ivalue = int.__new__(cls, value)
        if abs(ivalue) > 127:
            raise ValueError("Value must be between -127 and 127")
        return ivalue
