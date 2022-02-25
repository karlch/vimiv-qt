# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for exif handling.

All exif related tasks are implemented in this module. The heavy lifting is done using
one of the supported exif libraries, i.e.
* piexif (https://pypi.org/project/piexif/) and
* pyexiv2 (https://pypi.org/project/py3exiv2/).
"""

import contextlib
from pathlib import Path
import piexif
from typing import Any, Sequence, Iterable, Optional, Dict

from vimiv.imutils import exif
from vimiv.utils import log

_logger = log.module_logger(__name__)


def getMetadata(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return piexif.load(path)
    except FileNotFoundError:
        _logger.debug("File %s not found", path)
        return None
    except piexif.InvalidImageDataError:
        log.warning(
            "Piexif only supports the file types JPEG and TIFF.<br>\n"
            "Please use another backend for better file type support.<br>\n"
            "For more information see<br>\n"
            "https://karlch.github.io/vimiv-qt/documentation/exif.html",
            once=True,
        )
        return None


@exif.register(exif.Methods.get_formatted_metadata)
def get_formatted_metadata(path: Path, desired_keys: Sequence[str]) -> exif.ExifDictT:
    metadata = getMetadata(path)
    # TODO:  potentially remove
    desired_keys = [key.rpartition(".")[2] for key in desired_keys]
    exif = {}

    if metadata is None:
        return {}

    try:
        for ifd in metadata:
            if ifd == "thumbnail":
                continue

            for tag in metadata[ifd]:
                keyname = piexif.TAGS[ifd][tag]["name"]
                keytype = piexif.TAGS[ifd][tag]["type"]
                val = metadata[ifd][tag]
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

    except KeyError:
        return {}

    return exif


@exif.register(exif.Methods.get_keys)
def get_keys(path: Path) -> Iterable[str]:
    metadata = getMetadata(path)

    if metadata is None:
        return iter([])

    return (
        piexif.TAGS[ifd][tag]["name"]
        for ifd in metadata
        if ifd != "thumbnail"
        for tag in metadata[ifd]
    )


@exif.register(exif.Methods.copy_metadata)
def copy_metadata(path: Path, dest: str, reset_orientation: bool = True) -> None:
    metadata = getMetadata(path)

    if metadata is None:
        return

    try:
        if reset_orientation:
            with contextlib.suppress(KeyError):
                metadata["0th"][
                    piexif.ImageIFD.Orientation
                ] = exif.ExifOrientation.Normal
        exif_bytes = piexif.dump(metadata)
        piexif.insert(exif_bytes, dest)
        _logger.debug("Successfully wrote exif data for '%s'", dest)
    except ValueError:
        _logger.debug("No exif data in '%s'", dest)


@exif.register(exif.Methods.get_date_time)
def get_date_time(path: Path) -> str:
    metadata = getMetadata(path)

    if metadata is None:
        return ""

    with contextlib.suppress(KeyError):
        return metadata["0th"][piexif.ImageIFD.DateTime].decode()
    return ""


def init(*_args: Any, **_kwargs: Any) -> None:
    pass
