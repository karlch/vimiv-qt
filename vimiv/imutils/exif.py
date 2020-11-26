# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for exif handling.

All exif related tasks are implemented in this module. The heavy lifting is done using
piexif (https://github.com/hMatoba/Piexif).
"""

import contextlib
import itertools
from typing import Dict

from vimiv.utils import log, lazy
from vimiv import api

pyexiv2 = lazy.import_module("pyexiv2", optional=True)
piexif = lazy.import_module("piexif", optional=True)
_logger = log.module_logger(__name__)


def check_exif_dependancy(return_value=None, check_piexif=True):
    """Decorator for ExifHandler which require the optional py3exiv2 module.

    If py3exiv2 is available the class is left as it is. If py3exiv2 is not available
    but the depreciated piexif module is, a depreciation warning is given to the user
    and a ExifHandler class supporting piexif is returned. If none of the two modules
    is available, a dummy class is returned and a debug log is logged.

    Args:
        return_value: Value to return if neither py3exiv2 nor piexif is available.
        check_piexif: Check piexif dependency too in case py3exiv2 is not available.
    """

    def decorator(handler):
        if pyexiv2:
            return handler

        if piexif and check_piexif:

            class ExifHandlerPiexif(handler):
                """Depreciated handler to load and copy exif info. of a single image.

                This class provides several methods for interacting with metadata of a
                single image.

                Methods:
                    get_formatted_exif: Get dict containing formatted exif values.
                    copy_exif: Copies the metadata to the src image.
                    exif_date_time: Get the datetime.

                Attributes:
                    _metadata: Instance of the pyexiv2 metadata handler
                """

                def __init__(self, filename=""):
                    super()
                    self._metadata = None

                    try:
                        self._metadata = piexif.load(filename)
                    except FileNotFoundError:
                        _logger.debug("File %s not found", filename)
                        return

                def get_formatted_exif(self) -> Dict[str, str]:
                    """Get a dict of the formatted exif value.

                    Returns a dictionary contain formatted exif values for the exif tags
                    defined in the config.
                    """

                    desired_keys = [
                        e.strip()
                        for e in api.settings.metadata.current_keyset.value.split(",")
                    ]
                    _logger.debug(f"Read metadata.current_keys {desired_keys}")

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
                                    exif[keyname] = (keyname, val)
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
                        return None

                    return exif

                def copy_exif(self, dest: str, reset_orientation: bool = True) -> None:
                    """Copy exif information from current image to dest.

                    Args:
                        dest: Path to write the exif information to.
                        reset_orientation: If true, reset the exif orientation tag to
                            normal.
                    """

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
                        _logger.debug(
                            "File format for '%s' does not support exif", dest
                        )
                    except ValueError:
                        _logger.debug("No exif data in '%s'", dest)

                def exif_date_time(self) -> str:
                    """Exif creation date and time of filename."""

                    with contextlib.suppress(
                        piexif.InvalidImageDataError, FileNotFoundError, KeyError
                    ):
                        return self._metadata["0th"][piexif.ImageIFD.DateTime].decode()
                    return ""

            return ExifHandlerPiexif

        if return_value is not None:
            return return_value

        class NoExifHandler:
            """Handler for exif access without hander library."""

            def __init__(self, *args):
                _logger.debug("No exif support.")

            def copy_exif(self, *args) -> None:
                """Dummy handler for copy_exif."""
                _logger.debug(
                    "Cannot call '%s', py3exiv2 is required for exif support",
                    "copy_exif",
                )

            def exif_date_time(self, *args) -> None:
                """Dummy handler for exif_date_time."""
                _logger.debug(
                    "Cannot call '%s', py3exiv2 is required for exif support",
                    "exif_date_time",
                )
                return ""

            def get_formatted_exif(self, *args) -> None:
                """Dummy handler for get_formatted_exif."""
                _logger.debug(
                    "Cannot call '%s', py3exiv2 is required for exif support",
                    "get_formatted_exif",
                )

        return NoExifHandler

    return decorator


@check_exif_dependancy()
class ExifHandler:
    """Handler to load and copy exif information of a single image.

    This class provides several methods for interacting with metadata of a single image.

    Methods:
        get_formatted_exif: Get dict containing formatted exif values.
        copy_exif: Copies the metadata to the src image.
        exif_date_time: Get the datetime.

    Attributes:
        _metadata: Instance of the pyexiv2 metadata handler
    """

    def __init__(self, filename=""):

        try:
            self._metadata = pyexiv2.ImageMetadata(filename)
            self._metadata.read()

        except FileNotFoundError:
            _logger.debug("File %s not found", filename)
            return

    def get_formatted_exif(self) -> Dict[str, str]:
        """Get a dict of the formatted exif value.

        Returns a dictionary contain formatted exif values for the exif tags defined in
        the config.
        """

        desired_keys = [
            e.strip() for e in api.settings.metadata.current_keyset.value.split(",")
        ]
        _logger.debug(f"Read metadata.current_keys {desired_keys}")

        exif = dict()

        for base_key in desired_keys:
            # For backwards compability, assume it has one of the following prefixes
            for prefix in ["", "Exif.Image.", "Exif.Photo."]:
                key = f"{prefix}{base_key}"
                try:
                    key_name = self._metadata[key].name

                    try:
                        key_value = self._metadata[key].human_value

                    # Not all metadata(iptc) provide human_value, take raw_value instead
                    except AttributeError:
                        key_value = self._metadata[key].raw_value

                    exif[key] = (key_name, key_value)
                    break

                except KeyError:
                    _logger.debug("Key %s is invalid for the current image", key)
                    continue

        return exif

    def copy_exif(self, dest: str, reset_orientation: bool = True) -> None:
        """Copy exif information from current image to dest.

        Args:
            dest: Path to write the exif information to.
            reset_orientation: If true, reset the exif orientation tag to normal.
        """

        if reset_orientation:
            with contextlib.suppress(KeyError):
                self._metadata["Exif.Image.Orientation"] = ExifOrientation.Normal
        try:
            dest_image = pyexiv2.ImageMetadata(dest)
            dest_image.read()

            # File types restrict the metadata type they can store. Try copying all types one by one and skip if it fails.
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
        """Get exif creation date and time of filename."""

        with contextlib.suppress(KeyError):
            return self._metadata["Exif.Image.DateTime"].raw_value
        return ""


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
