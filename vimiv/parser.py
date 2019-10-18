# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""The commandline argument parser and related functions."""

import argparse
import logging
import os
from contextlib import suppress
from collections import namedtuple

import vimiv


def get_argparser() -> argparse.ArgumentParser:
    """Get the argparse parser."""
    parser = argparse.ArgumentParser(
        prog=vimiv.__name__, description=vimiv.__description__
    )
    parser.add_argument(
        "-f", "--fullscreen", action="store_true", help="Start fullscreen"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="store_true",
        help="Print version information and exit",
    )
    parser.add_argument(
        "-g",
        "--geometry",
        type=geometry,
        metavar="WIDTHxHEIGHT",
        help="Set the starting geometry",
    )
    parser.add_argument(
        "--temp-basedir", action="store_true", help="Use a temporary basedir"
    )
    parser.add_argument(
        "--config",
        type=existing_file,
        metavar="FILE",
        help="Use FILE as local configuration file",
    )
    parser.add_argument(
        "--keyfile",
        type=existing_file,
        metavar="FILE",
        help="Use FILE as keybinding file",
    )
    parser.add_argument(
        "-s",
        "--set",
        nargs=2,
        default=[],
        action="append",
        dest="cmd_settings",
        metavar=("OPTION", "VALUE"),
        help="Set a temporary setting",
    )
    parser.add_argument(
        "--log-level",
        type=loglevel,
        metavar="LEVEL",
        help="Set log level to LEVEL",
        default="info",
    )
    parser.add_argument(
        "--command",
        type=str,
        action="append",
        metavar="COMMAND",
        help="Run COMMAND on startup, usable multiple times",
    )
    parser.add_argument(
        "paths", nargs="*", type=existing_path, metavar="PATH", help="Paths to open"
    )

    devel = parser.add_argument_group("development arguments")
    devel.add_argument(
        "--debug",
        nargs="+",
        type=str,
        metavar="MODULE",
        default=(),
        help="Force showing debug log messages of MODULE",
    )
    return parser


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
        raise argparse.ArgumentTypeError(f"No file called '{value}'")
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
        raise argparse.ArgumentTypeError(f"No path called '{value}'")
    return value


def loglevel(value):
    """Check if an argument value is a valid log level.

    Args:
        value: Value given to command option as string.
    Returns:
        value as logging level.
    """
    with suppress(AttributeError):
        return getattr(logging, value.upper())
    raise argparse.ArgumentTypeError(f"Invalid log level '{value}'")
