# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions to be used by the argparse module as type.

Example for parsing commandline arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry", type=geometry)

Example for parsing vimiv command:
    argparser = argparse.ArgumentParser()
    argparser.add_argument("direction", type=scroll_direction)
"""

import argparse
import logging
import os
from enum import Enum
from collections import namedtuple

from vimiv.utils import ignore


def positive_int(value):
    """Check if an argument value is a positive int.

    Args:
        value: Value given to commandline option as string.
    Return:
        float(int) if the value is a positive int.
    """
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("Value must be positive")
    return ivalue


def positive_float(value):
    """Check if an argument value is a positive float.

    Args:
        value: Value given to commandline option as string.
    Return:
        float(value) if the value is a positive float.
    """
    fvalue = float(value)
    if fvalue <= 0:
        raise argparse.ArgumentTypeError("Value must be positive")
    return fvalue


Geometry = namedtuple("Geometry", ["width", "height"])


def geometry(value):
    """Check if an argument value is a valid geometry.

    Args:
        value: Value given to commandline option as string.
    Return:
        Tuple in the form of (height, width).
    """
    value = value.lower()  # Both x and X are allowed
    lvalue = value.split("x")
    if len(lvalue) != 2:
        raise argparse.ArgumentTypeError("Must be of the form WIDTHxHEIGHT")
    width = positive_int(lvalue[0])
    height = positive_int(lvalue[1])
    return Geometry(width, height)


def existing_file(value):
    """Check if an argument value is an existing file.

    Args:
        value: Value given to commandline option as string.
    Return:
        Path to the file as string if it exists.
    """
    if not os.path.isfile(os.path.expanduser(value)):
        raise argparse.ArgumentTypeError("No file called '%s'" % (value))
    return value


def existing_path(value):
    """Check if an argument value is an existing path.

    The difference to existing_file above is that this allows directories.

    Args:
        value: Value given to commandline option as string.
    Return:
        Path to the file as string if it exists.
    """
    if not os.path.exists(os.path.expanduser(value)):
        raise argparse.ArgumentTypeError("No path called '%s'" % (value))
    return value


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


class Direction(_ArgtypeEnum):
    Left = 0
    Right = 1
    Up = 2
    Down = 3


def scroll_direction(value):
    """Check if an argument value is a valid scroll direction.

    Args:
        value: Value given to command option as string.
    Returns:
        A Direction element if the value is valid.
    """
    return Direction.fromstr(value)


class Zoom(_ArgtypeEnum):
    In = 0
    Out = 1


def zoom(value):
    """Check if an argument value is a valid zoom.

    Args:
        value: Value given to command option as string.
    Returns:
        A Zoom element if the value is valid.
    """
    return Zoom.fromstr(value)


class LogLevel(_ArgtypeEnum):
    critical = logging.CRITICAL
    error = logging.ERROR
    warning = logging.WARNING
    info = logging.INFO
    debug = logging.DEBUG


def loglevel(value):
    """Check if an argument value is a valid log level.

    Args:
        value: Value given to command option as string.
    Return:
        value as logging level.
    """
    return LogLevel.fromstr(value).value


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


class HistoryDirection(_ArgtypeEnum):
    Next = 0
    Prev = 1


def command_history_direction(value):
    """Check if a value is a valid command history direction.

    Allowed: "next", "prev"

    Args:
        value: Value given to command option as string.
    Return:
        The value as HistoryDirection.
    """
    return HistoryDirection.fromstr(value)


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
