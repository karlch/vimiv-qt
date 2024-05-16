# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Metadata plugin provides all sort of information not provided by EXIF, IPTC, or XMP.

Properties:
- Get data not present in Exif, ICMP or XMP.
"""

import contextlib
from typing import Any, Sequence, Iterable, Optional, Dict, Tuple, Callable

from PyQt5.QtGui import QImageReader

from vimiv.imutils import metadata
from vimiv.utils import log, files

_logger = log.module_logger(__name__)


class MetadataGeneral(metadata.MetadataPlugin):
    """Provides all sort of information not provided by EXIF, IPTC, or XMP.

    Implements `get_metadata`, and `get_keys` only.
    """

    def __init__(self, path: str) -> None:
        self._path = path
        self._reader: Optional[QImageReader] = None

        # For each key, store (description, function)
        self._registry: Dict[str, Tuple[str, Callable]] = {
            "Vimiv.FileSize": ("File Size", self._get_filesize),
            "Vimiv.XDimension": (
                "Pixel X Dimension",
                self._get_xdimension,
            ),
            "Vimiv.YDimension": (
                "Pixel Y Dimension",
                self._get_ydimension,
            ),
            "Vimiv.FileType": ("File Type", self._get_filetype),
        }

    @staticmethod
    def name() -> str:
        """No backend is used, return plugin name."""
        return "general"

    @staticmethod
    def version() -> str:
        """No backend used, return empty string."""
        return ""

    @property
    def reader(self) -> QImageReader:
        """Return QImageReader instance of _path."""
        if self._reader is None:
            self._reader = QImageReader(self._path)
        return self._reader

    def get_metadata(self, desired_keys: Sequence[str]) -> metadata.MetadataDictT:
        """Get value of all desired keys for the current image."""
        out = {}

        for key in desired_keys:
            with contextlib.suppress(KeyError):
                desc, func = self._registry[key]
                out[key] = (desc, func())

        return out

    def get_keys(self) -> Iterable[str]:
        """Get the keys for all metadata values available for the current image."""
        return self._registry.keys()

    def _get_filesize(self) -> str:
        """Get the file size."""
        return files.get_size_file(self._path)

    def _get_filetype(self) -> str:
        """Get the file type."""
        out = files.imghdr.what(self._path)
        if out:
            return out
        return ""

    def _get_xdimension(self) -> str:
        """Get the x dimension in pixels.

        Does only works for image formats supported by QT natively.
        """
        return str(self.reader.size().width())

    def _get_ydimension(self) -> str:
        """Get the y dimension in pixels.

        Does only works for image formats supported by QT natively.
        """
        return str(self.reader.size().height())


def init(*_args: Any, **_kwargs: Any) -> None:
    """Register `MetadataGeneral` as a metadata handler."""
    metadata.register(MetadataGeneral)
