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
from pathlib import Path
from typing import Any, Sequence, Iterable, Optional

import pyexiv2

from vimiv.imutils import exif
from vimiv.utils import log, is_hex

_logger = log.module_logger(__name__)


def prepare_backend(path: Path) -> Optional[pyexiv2.ImageMetadata]:
    """Load metadata from image."""
    try:
        metadata = pyexiv2.ImageMetadata(path)
        metadata.read()
        return metadata
    except FileNotFoundError:
        _logger.debug("File %s not found", path)
        return None


@exif.register(exif.Operations.copy_metadata)
def copy_metadata(path: Path, dest: str, reset_orientation: bool = True) -> bool:
    """Copy metadata from current image to dest."""
    metadata = prepare_backend(path)

    if metadata is None:
        return False

    if reset_orientation:
        with contextlib.suppress(KeyError):
            metadata["Exif.Image.Orientation"] = exif.ExifOrientation.Normal

    try:
        dest_image = pyexiv2.ImageMetadata(dest)
        dest_image.read()

        # File types restrict the metadata type they can store.
        # Try copying all types one by one and skip if it fails.
        for copy_args in set(itertools.permutations((True, False, False, False))):
            with contextlib.suppress(ValueError):
                metadata.copy(dest_image, *copy_args)

        dest_image.write()
        return True
    except FileNotFoundError:
        _logger.debug("Failed to write metadata. Destination '%s' not found", dest)
    except OSError as e:
        _logger.debug("Failed to write metadata for '%s': '%s'", dest, str(e))
    return False


@exif.register(exif.Operations.get_date_time)
def get_date_time(path: Path) -> str:
    """Get creation date and time as formatted string."""
    metadata = prepare_backend(path)

    if metadata is None:
        return ""

    with contextlib.suppress(KeyError):
        return metadata["Exif.Image.DateTime"].raw_value
    return ""


@exif.register(exif.Operations.get_metadata)
def get_metadata(path: Path, desired_keys: Sequence[str]) -> exif.MetadataDictT:
    """Get value of all desired keys."""
    metadata = prepare_backend(path)
    out = {}

    if metadata is None:
        return {}

    for base_key in desired_keys:
        # TODO: potentially remove
        # For backwards compability, assume it has one of the following prefixes
        for prefix in ["", "Exif.Image.", "Exif.Photo."]:
            key = f"{prefix}{base_key}"
            try:
                key_name = metadata[key].name

                try:
                    key_value = metadata[key].human_value

                # Not all metadata (i.e. IPTC) provide human_value, take raw_value
                except AttributeError:
                    value = metadata[key].raw_value

                    # For IPTC the raw_value is a list of strings
                    if isinstance(value, list):
                        key_value = ", ".join(value)
                    else:
                        key_value = value

                out[key] = (key_name, key_value)
                break

            except KeyError:
                _logger.debug("Key %s is invalid for the current image", key)

    return out


@exif.register(exif.Operations.get_keys)
def get_keys(path: Path) -> Iterable[str]:
    """Retrieve the key of all metadata values available in the current image."""
    metadata = prepare_backend(path)

    if metadata is None:
        return iter([])

    return (key for key in metadata if not is_hex(key.rpartition(".")[2]))


def init(*_args: Any, **_kwargs: Any) -> None:
    pass
