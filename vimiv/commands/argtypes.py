# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
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
    return (width, height)


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


def scroll_direction(value):
    """Check if an argument value is a valid scroll direction.

    Args:
        value: Value given to command option as string.
    Return:
        value if the value is valid.
    """
    directions = ["left", "right", "up", "down"]
    if value not in directions:
        raise argparse.ArgumentTypeError(
            "Invalid scroll direction '{}'. Must be one of {}.".format(
                value, ", ".join(directions)))
    return value


def zoom(value):
    """Check if an argument value is a valid zoom.

    Args:
        value: Value given to command option as string.
    Return:
        value if the value is valid.
    """
    zooms = ["in", "out"]
    if value not in zooms:
        raise argparse.ArgumentTypeError(
            "Invalid zoom  '{}'. Must be one of {}.".format(
                value, ", ".join(zooms)))
    return value


def loglevel(value):
    """Check if an argument value is a valid log level.

    Args:
        value: Value given to command option as string.
    Return:
        value as logging level.
    """
    levels = ["debug", "info", "warning", "error", "critical"]
    value = value.lower()
    if value not in levels:
        raise argparse.ArgumentTypeError("Invalid loglevel  '%s'" % (value))
    if value == "critical":
        return logging.CRITICAL
    elif value == "error":
        return logging.ERROR
    elif value == "warning":
        return logging.WARNING
    elif value == "info":
        return logging.INFO
    return logging.DEBUG


def image_scale(value):
    """Check if value is a valid image scale.

    Allowed: "fit", "fit-width", "fit-height", positive_float.

    Args:
        value: Value given to command option as string.
    Return:
        value as image scale.
    """
    value = value.lower()
    if value in ["fit", "fit-width", "fit-height"]:
        return value
    return positive_float(value)
