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


def copy_exif(src: str, dest: str, reset_orientation: bool = True) -> None:
    """Copy exif information from src to dest.

    Args:
        src: Path to retrieve the exif information from.
        dest: Path to write the exif information to.
        reset_orientation: If true, reset the exif orientation tag to normal.
    """
    if piexif is None:  # No exif support
        logging.debug("copy_exif: Nothing to do as piexif not found")
        return
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
