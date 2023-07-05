# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Metadata plugin based on piexif (https://pypi.org/project/piexif/) backend.

Properties:
- Simple and easy to install.
- Limited image type support (JPG and TIFF only).
- No formatting of metadata.
- Can only handle Exif.
"""

import contextlib
from typing import Any, Sequence, Iterable

from vimiv.imutils import metadata
from vimiv.utils import log, lazy

piexif = lazy.import_module("piexif", optional=True)

_logger = log.module_logger(__name__)


class MetadataPiexif(metadata.MetadataPlugin):
    """Provided metadata support based on piexif.

    Implements `get_metadata`, `get_keys`, `copy_metadata`, and `get_date_time`.
    """

    def __init__(self, path: str) -> None:
        self._path = path

        try:
            self._metadata = piexif.load(path)
        except FileNotFoundError:
            _logger.debug("File %s not found", path)
            self._metadata = None
        except piexif.InvalidImageDataError:
            log.warning(
                "Piexif only supports the file types JPEG and TIFF.<br>\n"
                "Please use another metadata plugin for better file type support.<br>\n"
                "For more information see<br>\n"
                "https://karlch.github.io/vimiv-qt/documentation/metadata.html",
                once=True,
            )
            self._metadata = None

    @staticmethod
    def name() -> str:
        """Get the name of the used backend."""
        return "piexif"

    @staticmethod
    def version() -> str:
        """Get the version of the used backend."""
        return piexif.VERSION

    def get_metadata(self, desired_keys: Sequence[str]) -> metadata.MetadataDictT:
        """Get value of all desired keys for the current image."""
        out = {}

        # The keys in the default config are of the form `group.subgroup.key`. However,
        # piexif only uses `key` for the indexing. Strip `group.subgroup` prefix for the
        # metadata extraction, but maintain the long key in the returned dict.
        desired_keys_map = {key.rpartition(".")[2]: key for key in desired_keys}

        if self._metadata is None:
            return {}

        try:
            for ifd in self._metadata:
                if ifd == "thumbnail":
                    continue

                for tag in self._metadata[ifd]:
                    keyname = piexif.TAGS[ifd][tag]["name"]
                    keytype = piexif.TAGS[ifd][tag]["type"]
                    val = self._metadata[ifd][tag]
                    if keyname not in desired_keys_map:
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
                        out[desired_keys_map[keyname]] = (keyname, str(val))
                    elif keytype in (
                        piexif.TYPES.Ascii,
                        piexif.TYPES.Undefined,
                    ):  # byte encoded
                        out[desired_keys_map[keyname]] = (keyname, val.decode())
                    elif keytype in (
                        piexif.TYPES.Rational,
                        piexif.TYPES.SRational,
                    ):  # (int, int) <=> numerator, denominator
                        out[desired_keys_map[keyname]] = (keyname, f"{val[0]}/{val[1]}")

        except KeyError:
            return {}

        return out

    def get_keys(self) -> Iterable[str]:
        """Get the keys for all metadata values available for the current image."""
        if self._metadata is None:
            return iter([])

        return (
            piexif.TAGS[ifd][tag]["name"]
            for ifd in self._metadata
            if ifd != "thumbnail"
            for tag in self._metadata[ifd]
        )

    def copy_metadata(self, dest: str, reset_orientation: bool = True) -> bool:
        """Copy metadata from the current image to dest image."""
        if self._metadata is None:
            return False

        try:
            if reset_orientation:
                with contextlib.suppress(KeyError):
                    self._metadata["0th"][
                        piexif.ImageIFD.Orientation
                    ] = metadata.ExifOrientation.Normal
            exif_bytes = piexif.dump(self._metadata)
            piexif.insert(exif_bytes, dest)
            return True
        except ValueError:
            return False

    def get_date_time(self) -> str:
        """Get creation date and time of the current image as formatted string."""
        if self._metadata is None:
            return ""

        with contextlib.suppress(KeyError):
            return self._metadata["0th"][piexif.ImageIFD.DateTime].decode()
        return ""


def init(*_args: Any, **_kwargs: Any) -> None:
    """Initialize piexif handler if piexif is available."""
    if piexif is not None:
        metadata.register(MetadataPiexif)
    else:
        _logger.warning("Please install piexif to use this plugin")
