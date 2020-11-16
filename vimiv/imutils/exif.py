# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for exif handling.

All exif related tasks are implemented in this module. The heavy lifting is done using
piexif (https://github.com/hMatoba/Piexif).
"""

import contextlib

from vimiv.utils import log, lazy
from vimiv import api

pyexiv2 = lazy.import_module("pyexiv2", optional=True)
piexif = lazy.import_module("piexif", optional=True)

_logger = log.module_logger(__name__)


def check_pyexiv2(return_value=None):
    """Decorator for functions that require the optional pyexiv2 module.

    If pyexiv2 is not available, check if the depreciated piexif is available. If so, provide a warning to the user. If no module is available return_value is returned and a debug log message is
    logged. It it is available, the function is called as usual.

    Args:
        return_value: Value to return if neither pyexiv2 nor the depreciated piexif is available.
    """

    def decorator(func):
        def stub(*_args, **_kwargs):
            """Dummy function to call if pyexiv2 is not available."""
            _logger.debug(
                "Cannot call '%s', pyexiv2 is required for exif support", func.__name__
            )
            return return_value

        def stub_depreciate(*_args, **_kwargs):
            """Dummy function to call if pyexiv2 is not available but only the depreciated piexif."""
            _logger.warning("piexif is depreciated, please consider switching to exiv2")
            return return_value

        if pyexiv2 is None:
            if piexif is None:
                return stub

            return stub_depreciate

        return func

    return decorator


@check_pyexiv2()
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
            with contextlib.suppress(KeyError):
                exif_dict["0th"][piexif.ImageIFD.Orientation] = ExifOrientation.Normal
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, dest)
        _logger.debug("Succesfully wrote exif data for '%s'", dest)
    except piexif.InvalidImageDataError:  # File is not a jpg
        _logger.debug("File format for '%s' does not support exif", dest)
    except ValueError:
        _logger.debug("No exif data in '%s'", dest)


@check_pyexiv2("")
def exif_date_time(filename) -> str:
    """Exif creation date and time of filename."""
    with contextlib.suppress(piexif.InvalidImageDataError, FileNotFoundError, KeyError):
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
        self._metadata = None

        try:
            if pyexiv2 is None:
                if piexif is None:
                    log.error("%s relies on exif support", self.__class__.__qualname__)
                else:
                    log.error("piexif is depreciated, please consider switching to exiv2")

                    self._metadata = piexif.load(filename)
            else:
                self._metadata = pyexiv2.ImageMetadata(filename)
                self._metadata.read()

        except FileNotFoundError:
            _logger.debug("File %s not found", filename)
            return

        if self._metadata:
            self._load_exif()

    def _load_exif(self):
        """Load exif information from filename into the dictionary."""
        desired_keys = [
            e.strip()
            for e in api.settings.metadata.current_keyset.value.split(",")
        ]
        _logger.debug(f"Read metadata.current_keys {desired_keys}")

        try:  # Try using pyexiv2
            for key in desired_keys:
                try:
                    self[key] = (self._metadata[key].name, self._metadata[key].human_value)
                except AttributeError:
                    self[key] = (self._metadata[key].name, self._metadata[key].raw_value)
                except KeyError:
                    _logger.debug("Key %s is invalid for the current image", key)

        except AttributeError:  # pyexiv2 is not available
            try:

                for ifd in self._metadata:
                    if ifd == "thumbnail":
                        continue

                    for tag in self._metadata[ifd]:
                        keyname = piexif.TAGS[ifd][tag]["name"]
                        keytype = piexif.TAGS[ifd][tag]["type"]
                        val = self._metadata[ifd][tag]
                        _logger.debug(
                            f"name: {keyname} type: {keytype} value: {val} tag: {tag}"
                        )
                        if keyname.lower() not in desired_keys:
                            _logger.debug(f"Ignoring key {keyname}")
                            continue
                        if keytype in (
                            piexif.TYPES.Byte,
                            piexif.TYPES.Short,
                            piexif.TYPES.Long,
                            piexif.TYPES.SByte,
                            piexif.TYPES.SShort,
                            piexif.TYPES.SLong,
                            piexif.TYPES.Float,
                            piexif.TYPES.DFloat,
                        ):  # integer and float
                            self[keyname] = (keyname, val)
                        elif keytype in (
                            piexif.TYPES.Ascii,
                            piexif.TYPES.Undefined,
                        ):  # byte encoded
                            self[keyname] = (keyname, val.decode())
                        elif keytype in (
                            piexif.TYPES.Rational,
                            piexif.TYPES.SRational,
                        ):  # (int, int) <=> numerator, denominator
                            self[keyname] = (keyname, f"{val[0]}/{val[1]}")

            except (piexif.InvalidImageDataError, KeyError):
                return


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
