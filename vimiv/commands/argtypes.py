# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes to be used as custom types for vimiv commands..

Example for scroll direction:
    def scroll(self, direction: argtypes.Direction):
        ...
"""

import argparse
from enum import Enum

from vimiv.utils import ignore


class _ArgtypeEnum(Enum):
    """Enum with additional string functionality to be used by argparsers."""

    @staticmethod
    def tostr(elem):
        return elem.name.lower().replace("_", "-")

    @classmethod
    def allnames(cls):
        """Return all names neatly formatted."""
        return ", ".join("'%s'" % (cls.tostr(elem)) for elem in cls)

    @classmethod
    def fromstr(cls, name):
        """Create element from string name."""
        for elem in cls:
            if cls.tostr(elem) == name.lower():
                return elem
        raise argparse.ArgumentTypeError(
            "Invalid %s '%s'. Must be one of %s" % (
                cls.__name__, name, cls.allnames()))


class Direction(Enum):
    Left = "left"
    Right = "right"
    Up = "up"
    Down = "down"


class Zoom(Enum):
    In = "in"
    Out = "out"


class ImageScale(_ArgtypeEnum):
    Overzoom = 0
    Fit = 1
    Fit_Width = 2
    Fit_Height = 3

    @classmethod
    def fromstr(cls, name):
        """Override parent class to allow floats."""
        with ignore(ValueError):
            return float(name)
        return super().fromstr(name)


def image_scale(value):
    """Check if value is a valid image scale.

    Allowed: "overzoom", "fit", "fit-width", "fit-height", float.

    Args:
        value: Value given to command option as string.
    Return:
        The value as ImageScale.
    """
    return ImageScale.fromstr(value)


class HistoryDirection(Enum):
    Next = "next"
    Prev = "prev"


def manipulate_level(value):
    """Check if the value is a valid manipulation integer.

    Allowed: Any integer between -127 and 127.

    Args:
        value: Value given to command option as string.
    Return:
        The value if it was valid.
    """
    value = int(value)
    if value < -127 or value > 127:
        raise argparse.ArgumentTypeError("Value must be between -127 and 127")
    return value
