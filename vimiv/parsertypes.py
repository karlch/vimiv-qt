# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions used by the command line argument parser as type.

Example for parsing commandline arguments:
    parser = argparse.ArgumentParser()
    parser.add_argument("--geometry", type=parsertypes.geometry)
"""

import argparse
import logging
import os
from contextlib import suppress
from collections import namedtuple


def positive_int(value):
    """Check if an argument value is a positive int.

    Args:
        value: Value given to commandline option as string.
    Returns:
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
    Returns:
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
    Returns:
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
    Returns:
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
    Returns:
        Path to the file as string if it exists.
    """
    if not os.path.exists(os.path.expanduser(value)):
        raise argparse.ArgumentTypeError("No path called '%s'" % (value))
    return value


def loglevel(value):
    """Check if an argument value is a valid log level.

    Args:
        value: Value given to command option as string.
    Returns:
        value as logging level.
    """
    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    with suppress(KeyError):
        return log_levels[value.lower()]
    raise argparse.ArgumentTypeError("Invalid log level '%s'" % (value))
