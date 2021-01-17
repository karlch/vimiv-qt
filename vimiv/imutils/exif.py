# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for exif handling.

All exif related tasks are implemented in this module. The heavy lifting is done using
one of the supported exif libraries, i.e.
* piexif (https://pypi.org/project/piexif/) and
* pyexiv2 (https://pypi.org/project/py3exiv2/).
"""

import contextlib
import itertools
from typing import Any, Dict, Tuple, NoReturn, Sequence, Iterable

from vimiv.utils import log, lazy, is_hex

pyexiv2 = lazy.import_module("pyexiv2", optional=True)
piexif = lazy.import_module("piexif", optional=True)
_logger = log.module_logger(__name__)

ExifDictT = Dict[Any, Tuple[str, str]]


class UnsupportedExifOperation(NotImplementedError):
    """Raised if an exif operation is not supported by the used library if any."""


class _ExifHandlerBase:
    """Handler to load and copy exif information of a single image.

    This class provides the interface for handling exif support. By default none of the
    operations are implemented. Instead it is up to a child class which wraps around one
    of the supported exif libraries to implement the methods it can.
    """

    MESSAGE_SUFFIX = ". Please install pyexiv2 or piexif for exif support."

    def __init__(self, _filename=""):
        pass

    def copy_exif(self, _dest: str, _reset_orientation: bool = True) -> None:
        """Copy exif information from current image to dest.

        Args:
            dest: Path to write the exif information to.
            reset_orientation: If true, reset the exif orientation tag to normal.
        """
        self.raise_exception("Copying exif data")

    def exif_date_time(self) -> str:
        """Get exif creation date and time as formatted string."""
        self.raise_exception("Retrieving exif date-time")

    def get_formatted_exif(self, _desired_keys: Sequence[str]) -> ExifDictT:
        """Get a dictionary of formatted exif values."""
        self.raise_exception("Getting formatted exif data")

    def get_keys(self) -> Iterable[str]:
        """Retrieve the name of all exif keys available."""
        self.raise_exception("Getting exif keys")

    @classmethod
    def raise_exception(cls, operation: str) -> NoReturn:
        """Raise an exception for a not implemented exif operation."""
        msg = f"{operation} is not supported{cls.MESSAGE_SUFFIX}"
        _logger.warning(msg, once=True)
        raise UnsupportedExifOperation(msg)


class _ExifHandlerPiexif(_ExifHandlerBase):
    """Implementation of ExifHandler based on piexif."""

    MESSAGE_SUFFIX = " by piexif."

    def __init__(self, filename=""):
        super().__init__(filename)
        try:
            self._metadata = piexif.load(filename)
        except FileNotFoundError:
            _logger.debug("File %s not found", filename)
            self._metadata = None

    def get_formatted_exif(self, desired_keys: Sequence[str]) -> ExifDictT:
        desired_keys = [key.rpartition(".")[2] for key in desired_keys]
        exif = dict()

        try:
            for ifd in self._metadata:
                if ifd == "thumbnail":
                    continue

                for tag in self._metadata[ifd]:
                    keyname = piexif.TAGS[ifd][tag]["name"]
                    keytype = piexif.TAGS[ifd][tag]["type"]
                    val = self._metadata[ifd][tag]
                    _logger.debug(
                        f"name: {keyname}\
                        type: {keytype}\
                        value: {val}\
                        tag: {tag}"
                    )
                    if keyname not in desired_keys:
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
                        exif[keyname] = (keyname, str(val))
                    elif keytype in (
                        piexif.TYPES.Ascii,
                        piexif.TYPES.Undefined,
                    ):  # byte encoded
                        exif[keyname] = (keyname, val.decode())
                    elif keytype in (
                        piexif.TYPES.Rational,
                        piexif.TYPES.SRational,
                    ):  # (int, int) <=> numerator, denominator
                        exif[keyname] = (keyname, f"{val[0]}/{val[1]}")

        except (piexif.InvalidImageDataError, KeyError):
            return {}

        return exif

    def get_keys(self) -> Iterable[str]:
        return (
            piexif.TAGS[ifd][tag]["name"]
            for ifd in self._metadata
            if ifd != "thumbnail"
            for tag in self._metadata[ifd]
        )

    def copy_exif(self, dest: str, reset_orientation: bool = True) -> None:
        try:
            if reset_orientation:
                with contextlib.suppress(KeyError):
                    self._metadata["0th"][
                        piexif.ImageIFD.Orientation
                    ] = ExifOrientation.Normal
            exif_bytes = piexif.dump(self._metadata)
            piexif.insert(exif_bytes, dest)
            _logger.debug("Successfully wrote exif data for '%s'", dest)
        except piexif.InvalidImageDataError:  # File is not a jpg
            _logger.debug("File format for '%s' does not support exif", dest)
        except ValueError:
            _logger.debug("No exif data in '%s'", dest)

    def exif_date_time(self) -> str:
        with contextlib.suppress(
            piexif.InvalidImageDataError, FileNotFoundError, KeyError
        ):
            return self._metadata["0th"][piexif.ImageIFD.DateTime].decode()
        return ""


def check_exif_dependancy(handler):
    """Decorator for ExifHandler which requires the optional pyexiv2 module.

    If pyexiv2 is available, the class is left as it is. If pyexiv2 is not available
    but the less powerful piexif module is, _ExifHandlerPiexif is returned instead.
    If none of the two modules are available, the base implementation which always
    throws an exception is returned.

    Args:
        handler: The class to be decorated.
    """
    if pyexiv2:
        return handler

    if piexif:
        return _ExifHandlerPiexif

    _logger.warning(
        "There is no exif support and therefore:\n"
        "1. Exif data is lost when writing images to disk.\n"
        "2. The `:metadata` command and associated `i` keybinding is not available.\n"
        "3. The {exif-date-time} statusbar module is not available."
    )

    return _ExifHandlerBase


@check_exif_dependancy
class ExifHandler(_ExifHandlerBase):
    """Main ExifHandler implementation based on pyexiv2."""

    MESSAGE_SUFFIX = " by pyexiv2."

    def __init__(self, filename=""):
        super().__init__(filename)
        try:
            self._metadata = pyexiv2.ImageMetadata(filename)
            self._metadata.read()
        except FileNotFoundError:
            _logger.debug("File %s not found", filename)

    def get_formatted_exif(self, desired_keys: Sequence[str]) -> ExifDictT:
        exif = dict()

        for base_key in desired_keys:
            # For backwards compability, assume it has one of the following prefixes
            for prefix in ["", "Exif.Image.", "Exif.Photo."]:
                key = f"{prefix}{base_key}"
                try:
                    key_name = self._metadata[key].name

                    try:
                        key_value = self._metadata[key].human_value

                    # Not all metadata (i.e. IPTC) provide human_value, take raw_value
                    except AttributeError:
                        value = self._metadata[key].raw_value

                        # For IPTC the raw_value is a list of strings
                        if isinstance(value, list):
                            key_value = ", ".join(value)
                        else:
                            key_value = value

                    exif[key] = (key_name, key_value)
                    break

                except KeyError:
                    _logger.debug("Key %s is invalid for the current image", key)

        return exif

    def get_keys(self) -> Iterable[str]:
        return (key for key in self._metadata if not is_hex(key.rpartition(".")[2]))

    def copy_exif(self, dest: str, reset_orientation: bool = True) -> None:
        if reset_orientation:
            with contextlib.suppress(KeyError):
                self._metadata["Exif.Image.Orientation"] = ExifOrientation.Normal
        try:
            dest_image = pyexiv2.ImageMetadata(dest)
            dest_image.read()

            # File types restrict the metadata type they can store.
            # Try copying all types one by one and skip if it fails.
            for copy_args in set(itertools.permutations((True, False, False, False))):
                with contextlib.suppress(ValueError):
                    self._metadata.copy(dest_image, *copy_args)

            dest_image.write()

            _logger.debug("Successfully wrote exif data for '%s'", dest)
        except FileNotFoundError:
            _logger.debug("Failed to write exif data. Destination '%s' not found", dest)
        except OSError as e:
            _logger.debug("Failed to write exif data for '%s': '%s'", dest, str(e))

    def exif_date_time(self) -> str:
        with contextlib.suppress(KeyError):
            return self._metadata["Exif.Image.DateTime"].raw_value
        return ""


has_exif_support = ExifHandler != _ExifHandlerBase


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
