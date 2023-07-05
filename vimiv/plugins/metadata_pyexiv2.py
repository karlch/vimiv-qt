# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Metadata plugin based on pyexiv2 (https://pypi.org/project/py3exiv2/) backend.

Properties:
- Shared libraries as dependencies.
- Formatted Metadata.
- Reads Exif, IPTC and XMP.
"""

import contextlib
import itertools
from typing import Any, Sequence, Iterable

from vimiv.imutils import metadata
from vimiv.utils import log, is_hex, lazy

pyexiv2 = lazy.import_module("pyexiv2", optional=True)

_logger = log.module_logger(__name__)


class MetadataPyexiv2(metadata.MetadataPlugin):
    """Provides metadata support based on pyexiv2."""

    def __init__(self, path: str) -> None:
        self._path = path

        try:
            self._metadata = pyexiv2.ImageMetadata(path)
            self._metadata.read()
        except FileNotFoundError:
            _logger.debug("File %s not found", path)
            self._metadata = None

    @staticmethod
    def name() -> str:
        """Get the name of the used backend."""
        return "pyexiv2"

    @staticmethod
    def version() -> str:
        """Get the version of the used backend."""
        return pyexiv2.__version__

    def get_metadata(self, desired_keys: Sequence[str]) -> metadata.MetadataDictT:
        """Get value of all desired keys for the current image."""

        out = {}

        if self._metadata is None:
            return {}

        for key in desired_keys:
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

                out[key] = (key_name, key_value)

            except KeyError:
                _logger.debug("Key %s is invalid for the current image", key)

        return out

    def get_keys(self) -> Iterable[str]:
        """Get the keys for all metadata values available for the current image."""
        if self._metadata is None:
            return iter([])

        return (key for key in self._metadata if not is_hex(key.rpartition(".")[2]))

    def copy_metadata(self, dest: str, reset_orientation: bool = True) -> bool:
        """Copy metadata from the current image to dest image."""
        if self._metadata is None:
            return False

        if reset_orientation:
            with contextlib.suppress(KeyError):
                self._metadata[
                    "Exif.Image.Orientation"
                ] = metadata.ExifOrientation.Normal

        try:
            dest_image = pyexiv2.ImageMetadata(dest)
            dest_image.read()

            # File types restrict the metadata type they can store.
            # Try copying all types one by one and skip if it fails.
            for copy_args in set(itertools.permutations((True, False, False, False))):
                with contextlib.suppress(ValueError):
                    self._metadata.copy(dest_image, *copy_args)

            dest_image.write()
            return True
        except FileNotFoundError:
            _logger.debug("Failed to write metadata. Destination '%s' not found", dest)
        except OSError as e:
            _logger.debug("Failed to write metadata for '%s': '%s'", dest, str(e))
        return False

    def get_date_time(self) -> str:
        """Get creation date and time of the current image as formatted string."""
        if self._metadata is None:
            return ""

        with contextlib.suppress(KeyError):
            return self._metadata["Exif.Image.DateTime"].raw_value
        return ""


def init(*_args: Any, **_kwargs: Any) -> None:
    """Initialize pyexiv2 handler if pyexiv2 is available."""
    if pyexiv2 is not None:
        metadata.register(MetadataPyexiv2)
    else:
        _logger.warning("Please install py3exiv2 to use this plugin")
