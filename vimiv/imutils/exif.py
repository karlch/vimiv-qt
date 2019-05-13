# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for exif handling.

All exif related tasks are implemented in this module. The heavy lifting is done using
piexif (https://github.com/hMatoba/Piexif).
"""

import logging
from contextlib import suppress

# We need the check as exif support is optional
try:
    import piexif
except ImportError:
    piexif = None


def check_piexif(return_value=None):
    """Decorator for functions that require the optional piexif module.

    If piexif is not available, return_value is returned and a debug log message is
    logged. It it is availabel, the function is called as usual.

    Args:
        return_value: Value to return if piexif is not available.
    """

    def decorator(func):
        def stub(*args, **kwargs):
            """Dummy function to call if piexif is not available."""
            logging.debug(
                "Cannot call '%s', piexif is required for exif support", func.__name__
            )
            return return_value

        if piexif is None:
            return stub
        return func

    return decorator


@check_piexif()
def copy_exif(src: str, dest: str, reset_orientation: bool = True) -> None:
    """Copy exif information from src to dest.

    Args:
        src: Path to retrieve the exif information from.
        dest: Path to write the exif information to.
        reset_orientation: If true, reset the exif orientation tag to normal.
    """
    try:
        exif_dict = piexif.load(src)
        if reset_orientation:
            with suppress(KeyError):
                exif_dict["0th"][piexif.ImageIFD.Orientation] = ExifOrientation.Normal
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, dest)
        logging.debug("Succesfully wrote exif data for '%s'", dest)
    except piexif.InvalidImageDataError:  # File is not a jpg
        logging.debug("File format for '%s' does not support exif", dest)
    except ValueError:
        logging.debug("No exif data in '%s'", dest)


@check_piexif("")
def exif_date_time(filename) -> str:
    """Exif creation date and time of filename."""
    with suppress(piexif.InvalidImageDataError, FileNotFoundError, KeyError):
        exif_dict = piexif.load(filename)
        return exif_dict["0th"][piexif.ImageIFD.DateTime].decode()


class ExifOrientation:
    """Namespace for exif orientation tags.

    For more information see: http://jpegclub.org/exif_orientation.html.
    """

    Unspecified = 0
    Normal = 1
    HorizontalFlip = 2
    Rotation180 = 3
    VerticalFlip = 4
    Rotation90HorizontalFlip = 5
    Rotation90 = 6
    Rotation90VerticalFlip = 7
    Rotation270 = 8
