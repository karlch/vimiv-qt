# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for exif handling.

All exif related tasks are implemented in this module. The heavy lifting is done using
piexif (https://github.com/hMatoba/Piexif).
"""

from contextlib import suppress

from vimiv.utils import log

# We need the check as exif support is optional
try:
    import piexif
except ImportError:  # pragma: no cover  # Covered in a different tox env during CI
    piexif = None


_logger = log.module_logger(__name__)


def check_piexif(return_value=None):
    """Decorator for functions that require the optional piexif module.

    If piexif is not available, return_value is returned and a debug log message is
    logged. It it is availabel, the function is called as usual.

    Args:
        return_value: Value to return if piexif is not available.
    """

    def decorator(func):
        def stub(*_args, **_kwargs):
            """Dummy function to call if piexif is not available."""
            _logger.debug(
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
        _logger.debug("Succesfully wrote exif data for '%s'", dest)
    except piexif.InvalidImageDataError:  # File is not a jpg
        _logger.debug("File format for '%s' does not support exif", dest)
    except ValueError:
        _logger.debug("No exif data in '%s'", dest)


@check_piexif("")
def exif_date_time(filename) -> str:
    """Exif creation date and time of filename."""
    with suppress(piexif.InvalidImageDataError, FileNotFoundError, KeyError):
        exif_dict = piexif.load(filename)
        return exif_dict["0th"][piexif.ImageIFD.DateTime].decode()
    return ""


class ExifInformation(dict):
    """Dictionary to load and store exif information of a single image.

    Exif information is loaded and formatted upon construction. Afterwards the class
    behaves like a regular dictionary.

    Attributes:
        _exif: Loaded piexif exif information dictionary if any.
    """

    def __init__(self, filename):
        super().__init__()
        self._exif = None

        if piexif is None:
            log.error("%s relies on exif support", self.__class__.__qualname__)
        else:
            self._load_exif(filename)

    def _load_exif(self, filename):
        """Load exif information from filename into the dictionary."""
        try:
            self._exif = piexif.load(filename)
        except (piexif.InvalidImageDataError, FileNotFoundError, KeyError):
            return
        # Read information from 0th IFD
        ifd = piexif.ImageIFD
        self._add_bytes_info("Make", "0th", ifd.Make)
        self._add_bytes_info("Model", "0th", ifd.Model)
        self._add_bytes_info("DateTime", "0th", ifd.DateTime)
        # Read information from Exif IFD
        ifd = piexif.ExifIFD
        self._add_two_digits("ExposureTime", "Exif", ifd.ExposureTime, suffix=" s")
        self._add_fraction("FNumber", "Exif", ifd.FNumber, prefix="f/")
        self._add_fraction("ShutterSpeedValue", "Exif", ifd.ShutterSpeedValue, " EV")
        self._add_fraction("ApertureValue", "Exif", ifd.ApertureValue, " EV")
        self._add_fraction("ExposureBiasValue", "Exif", ifd.ExposureBiasValue, " EV")
        self._add_fraction("FocalLength", "Exif", ifd.FocalLength, " mm")
        _logger.debug("%s initialized, content:\n%r", self.__class__.__qualname__, self)

    def _add_bytes_info(self, name, ifd, key):
        """Add exif information of type bytes to the dictionary."""
        with suppress(KeyError):
            self[name] = self._exif[ifd][key].decode()

    def _add_fraction(self, name, ifd, key, suffix="", prefix=""):
        """Add exif information as fraction of two numbers to the dictionary."""
        with suppress(KeyError):
            value_tuple = self._exif[ifd][key]
            fraction = value_tuple[0] / value_tuple[1]
            self[name] = f"{prefix}{fraction:.2f}{suffix}"

    def _add_two_digits(self, name, ifd, key, separator="/", suffix="", prefix=""):
        """Add exif information as two numbers to the dictionary."""
        with suppress(KeyError):
            value_tuple = self._exif[ifd][key]
            self[name] = f"{prefix}%s{separator}%s{suffix}" % value_tuple


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
