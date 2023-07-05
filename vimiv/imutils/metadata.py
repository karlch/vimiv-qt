# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for metadata handling.

This module provides a common interface for all metadata related functionalities.
`MetadataHandler` is used to interact with the metadata of the current image. It
relies on the functionality provided by optionally loaded metadata plugins. Such
plugins implements the `MetadataPlugin` abstract class and registers that class
using the `register` function.

Module Attributes:
    _registry: List of registered `MetadataPlugin` implementations.
"""

import abc
import contextlib
import itertools
from typing import Dict, Tuple, NoReturn, Sequence, Iterable, Type, List

from vimiv.utils import log

_logger = log.module_logger(__name__)

# Type returned by `MetadataHandler.get_metadata`.
# Key is the metadata key. Value is a tuple of descriptive name and value for that key.
MetadataDictT = Dict[str, Tuple[str, str]]


class MetadataPlugin(abc.ABC):
    """Abstract class implemented by plugins to provide metadata capabilities.

    Implementations of this class are required to overwrite `__init__`, `name`,
    `version`, `get_metadata` and `get_keys`.
    The implementation of `copy_metadata` and `get_date_time` is optional.
    """

    @abc.abstractmethod
    def __init__(self, _path: str) -> None:
        """Initialize metadata handler for a specific image.

        Args:
            _path: Path to current image.
        """

    @staticmethod
    @abc.abstractmethod
    def name() -> str:
        """Get the name of the used backend.

        If no backend is used, return the name of the plugin.
        """

    @staticmethod
    @abc.abstractmethod
    def version() -> str:
        """Get the version of the used backend.

        If no backend is used, return an empty string.
        """

    @abc.abstractmethod
    def get_metadata(self, _keys: Sequence[str]) -> MetadataDictT:
        """Get value of all desired keys for the current image.

        If no value is found for a certain key, do not include the key in the output.

        Args:
            _keys: Keys of metadata to query the image for.

        Returns:
            Dictionary with retrieved metadata.
        """

    @abc.abstractmethod
    def get_keys(self) -> Iterable[str]:
        """Get the keys for all metadata values available for the current image."""

    def copy_metadata(self, _dest: str, _reset_orientation: bool = True) -> bool:
        """Copy metadata from the current image to dest image.

        Args:
            _dest: Path to write the metadata to.
            _reset_orientation: If true, reset the exif orientation tag to normal.

        Returns:
            Flag indicating if copy was successful.
        """
        raise NotImplementedError

    def get_date_time(self) -> str:
        """Get creation date and time of the current image as formatted string."""
        raise NotImplementedError


# Stores all registered metadata implementations.
_registry: List[Type[MetadataPlugin]] = []


def has_metadata_support() -> bool:
    """Indicate if `MetadataHandler` has `get_metadata()` and `get_keys()` capabilities.

    Returns:
        True if at least one metadata plugins has been registered.
    """
    return bool(_registry)


class MetadataHandler:
    """Handle metadata related functionalities of images.

    Attributes:
        _path: Path to current image.
    """

    def __init__(self, path: str):
        self._path = path

    @property
    def has_copy_metadata(self) -> bool:
        """True if `MetadataHandler` has an implementation for `copy_metadata`."""
        return any(e.copy_metadata != MetadataPlugin.copy_metadata for e in _registry)

    @property
    def has_get_date_time(self) -> bool:
        """True if `MetadataHandler` has an implementation for `get_date_time`."""
        return any(e.get_date_time != MetadataPlugin.get_date_time for e in _registry)

    def get_metadata(self, keys: Sequence[str]) -> MetadataDictT:
        """Get value of all desired keys from the current image.

        Use all registered metadata implementations to extract the metadata from the
        current image. The output of all methods is combined.

        Args:
            keys: Keys of metadata to query the image for.

        Returns:
            Dictionary with retrieved metadata.

        Raises:
            MetadataError
        """
        if not has_metadata_support():
            MetadataHandler.raise_exception("get_metadata")

        out: MetadataDictT = {}

        for backend in _registry:
            # TODO: from 3.9 on use: c = a | b
            out = {**backend(self._path).get_metadata(keys), **out}

        return out

    def get_keys(self) -> Iterable[str]:
        """Get the keys for all metadata values available for the current image.

        Uses all registered metadata implementations to extract the available keys for
        the current image. The output of all methods is combined.

        Raises:
            MetadataError
        """
        if not has_metadata_support():
            MetadataHandler.raise_exception("get_keys")

        out: Iterable[str] = iter([])

        for backend in _registry:
            out = itertools.chain(out, backend(self._path).get_keys())

        return out

    def copy_metadata(self, dest: str, reset_orientation: bool = True) -> None:
        """Copy metadata from current image to dest.

        Uses all registered metadata implementations that support this operation.

        Args:
            dest: Path to write the metadata to.
            reset_orientation: If true, reset the exif orientation tag to normal.

        Raises:
            MetadataError
        """
        if not has_metadata_support() or not self.has_copy_metadata:
            MetadataHandler.raise_exception("copy_metadata")

        failed = []

        for backend in _registry:
            with contextlib.suppress(NotImplementedError):
                be = backend(self._path)
                if not be.copy_metadata(dest, reset_orientation):
                    failed.append(be.name())

        if failed:
            _logger.warning(
                f"The following plugins failed to copy metadata: "
                f"{', '.join(failed)}<br>\n"
                f"Some metadata may be missing in the destination image {dest}."
            )

    def get_date_time(self) -> str:
        """Get creation date and time as formatted string.

        Uses the first registered metadata implementations that supports this operation.

        Raises:
            MetadataError
        """
        if not has_metadata_support() or not self.has_get_date_time:
            MetadataHandler.raise_exception("get_date_time")

        for backend in _registry:
            with contextlib.suppress(NotImplementedError):
                out = backend(self._path).get_date_time()
                # If we get an empty string, continue. We may get something better.
                if out:
                    return out
        return ""

    @staticmethod
    def raise_exception(operation: str) -> NoReturn:
        """Raise an exception if there is insufficient support for an operation."""
        msg = f"Running {operation} is not possible. Insufficient metadata support"
        _logger.warning(msg, once=True)
        raise MetadataError(msg)


class MetadataError(RuntimeError):
    """Raised if for a function there is insufficient metadata support."""


def register(plugin: Type[MetadataPlugin]) -> None:
    """Register metadata plugin implementation.

    All registered metadata plugin implementations are available to the
    `MetadataHandler`.

    Args:
        plugin: Implementation of `MetadataPlugin`.
    """

    _logger.debug(f"Registring metadata plugin implementation {plugin.name()}")
    if plugin in _registry:
        _logger.warning(
            f"Metadata plugin {plugin.name()} has already been registered. Ignoring it."
        )
        return

    _registry.append(plugin)


def get_registrations() -> List[Tuple[str, str]]:
    """List of all registered metadata plugin implementations.

    Returns:
        List of tuples of the form (name of backend, version of backend).
    """
    return [(e.name(), e.version()) for e in _registry]


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
