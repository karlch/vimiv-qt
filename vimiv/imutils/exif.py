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

piexif = lazy.import_module("piexif", optional=True)

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
            with contextlib.suppress(KeyError):
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
        self._exif = None

        if piexif is None:
            log.error("%s relies on exif support", self.__class__.__qualname__)
        else:
            self._load_exif(filename)

    def _load_exif(self, filename):
        """Load exif information from filename into the dictionary."""
        try:
            self._exif = piexif.load(filename)
            desiredKeys = [e.lower().strip() for e in api.settings.get_value("metadata.keylist").split(',')]
            _logger.debug(f'Read metadata.keylist {desiredKeys}')
        except (piexif.InvalidImageDataError, FileNotFoundError, KeyError):
            return

        for ifd in self._exif:
            if ifd == "thumbnail":
                continue

            for tag in self._exif[ifd]:
                keyname = piexif.TAGS[ifd][tag]["name"]
                keytype = piexif.TAGS[ifd][tag]["type"]
                val = self._exif[ifd][tag]
                _logger.debug(f'name: {keyname} type: {keytype} value: {val} tag: {tag}')
                if keyname.lower() not in desiredKeys:
                    _logger.debug(f'{keyname.lower()} not in {desiredKeys}. Ignoring it')
                    continue
                if keytype in (1, 3, 4, 9): # integer
                    with contextlib.suppress(KeyError):
                        self[keyname] = val
                elif keytype == 2: # byte encoded ascii
                    with contextlib.suppress(KeyError):
                        self[keyname] = val.decode()
                elif keytype in (5, 10): # (int, int) <=> numerator, denominator
                    with contextlib.suppress(KeyError):
                        self[keyname] = f"{val[0]}/{val[1]}"
                elif keytype == 7: # byte
                    with contextlib.suppress(KeyError):
                        self[keyname] = val.decode()


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
