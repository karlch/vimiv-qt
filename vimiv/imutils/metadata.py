# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Utility functions and classes for metadata handling.

This module provides a common interface for all metadata related functionalities.
Metadata plugins provide metadata for the current image by registering function
implementations for the functions specified by `Operations`. Registered implementations
are stored in the `_MetadataRegistry`. The `MetadataHandler` is the main class used
to interact with the metadata of the current image. It queries `_MetadataRegistry`
and uses the registering implementations to provide its functionality.

Module Attributes:
    _registry: Dictionary storing function implementations for all operations.
"""

import contextlib
import itertools
import inspect
from typing import Dict, Tuple, NoReturn, Sequence, Iterable, Type, Optional

from vimiv.utils import log

_logger = log.module_logger(__name__)

# Type returned by `MetadataHandler.get_metadata`. Key if dictionary is the metadata
# key. Value is a tuple of name and value for that key.
MetadataDictT = Dict[str, Tuple[str, str]]


class MetadataPlugin:
    """Base class overwritten by plugins to extend the metadata capabilities."""

    # Fields must be set by any subclass
    name: Optional[str] = None
    version: Optional[str] = None

    def __init__(self, path: str) -> None:
        self._path = path

    def __init_subclass__(cls, **kwargs):
        """Enforce subclasses to set attribute `name` and `version`."""
        for required in ("name", "version"):
            if not getattr(cls, required):
                raise TypeError(
                    f"Cannot instantiate {cls.__name__} "
                    f"without {required} attribute defined"
                )
        return super().__init_subclass__(**kwargs)

    def copy_metadata(self, _dest: str, _reset_orientation: bool = True) -> bool:
        """Copy metadata from current image to dest.

        Args:
            dest: Path to write the metadata to.
            reset_orientation: If true, reset the exif orientation tag to normal.

        Returns:
            Flag indicating if copy was successful.
        """
        raise NotImplementedError

    def get_date_time(self) -> str:
        """Get creation date and time as formatted string."""
        raise NotImplementedError

    def get_metadata(self, _keys: Sequence[str]) -> MetadataDictT:
        """Get value of all desired keys.

        Args:
            keys: Keys of metadata to query the image for.

        Returns:
            Dictionary with retrieved metadata.
        """
        raise NotImplementedError

    def get_keys(self) -> Iterable[str]:
        """Retrieve the key of all metadata values available in the current image."""
        raise NotImplementedError

    @classmethod
    def _implement_copy_metadata(cls) -> bool:
        """Return True iff class overwrites `MetadataPlugin.copy_metadata`."""
        return cls.copy_metadata != MetadataPlugin.copy_metadata

    @classmethod
    def _implement_get_date_time(cls) -> bool:
        """Return True iff class overwrites `MetadataPlugin.get_date_time`."""
        return cls.get_date_time != MetadataPlugin.get_date_time

    @classmethod
    def _implement_get_metadata(cls) -> bool:
        """Return True iff class overwrites `MetadataPlugin.get_metadata`."""
        return cls.get_metadata != MetadataPlugin.get_metadata

    @classmethod
    def _implement_get_keys(cls) -> bool:
        """Return True iff class overwrites `MetadataPlugin.get_keys`."""
        return cls.get_keys != MetadataPlugin.get_keys


class _MetadataRegistry(dict):
    """Handles the registration of function implementations."""


    def __init__(self):
        super().__init__()
        _logger.debug("Initializing metadata registry")
        self.has_copy_metadata = False
        self.has_get_date_time = False
        self.has_get_metadata = False
        self.has_get_keys = False

    def __setitem__(self, key: str, val: Type[MetadataPlugin]):

        if val._implement_copy_metadata():
            self.has_copy_metadata = True

        if val._implement_get_date_time():
            self.has_get_date_time = True

        if val._implement_get_metadata():
            self.has_get_metadata = True

        if val._implement_get_keys():
            self.has_get_keys = True

        dict.__setitem__(self, key, val)


_registry: _MetadataRegistry = _MetadataRegistry()


def has_copy_metadata() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `copy_metadata`."""
    return _registry.has_copy_metadata


def has_get_date_time() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `get_date_time`."""
    return _registry.has_get_date_time


def has_get_metadata() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `get_metadata`."""
    return _registry.has_get_metadata


def has_get_keys() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `get_keys`."""
    return _registry.has_get_keys


class MetadataHandler:
    """Handle metadata related functionalities of images.

    Attributes:
        _path: Path to current image.
    """

    def __init__(self, path: str):
        self._path = path

    def copy_metadata(self, dest: str, reset_orientation: bool = True) -> None:
        """Copy metadata from current image to dest.

        Runs all registered implementations for `Operations.copy_metadata`.

        Args:
            dest: Path to write the metadata to.
            reset_orientation: If true, reset the exif orientation tag to normal.
        """

        if not has_copy_metadata():
            MetadataHandler.raise_exception()

        failed = []

        for name, backend in _registry.items():
            with contextlib.suppress(NotImplementedError):
                if not backend(self._path).copy_metadata(dest, reset_orientation):
                    failed.append(name)

        if failed:
            _logger.warning(
                f"The following plugins failed to copy metadata: "
                f"{', '.join(failed)}<br>\n"
                f"Some metadata may be missing in the destination image {dest}."
            )

    def get_date_time(self) -> str:
        """Get creation date and time as formatted string."""

        if not has_get_date_time():
            MetadataHandler.raise_exception()

        for _, backend in _registry.items():
            with contextlib.suppress(NotImplementedError):
                return backend(self._path).get_date_time()
        return ""

    def get_metadata(self, keys: Sequence[str]) -> MetadataDictT:
        """Get value of all desired keys.

        Use all registered implementations for `Operations.get_metadata` to query
        the current image using the provided metadata keys. The result of all
        implementations is combined.

        Args:
            keys: Keys of metadata to query the image for.

        Returns:
            Dictionary with retrieved metadata.
        """

        if not has_get_metadata():
            MetadataHandler.raise_exception()

        out: MetadataDictT = {}

        for _, backend in _registry.items():
            with contextlib.suppress(NotImplementedError):
                # TODO: from 3.9 on use: c = a | b
                out = {**backend(self._path).get_metadata(keys), **out}

        return out

    def get_keys(self) -> Iterable[str]:
        """Retrieve the key of all metadata values available in the current image."""

        if not has_get_keys():
            MetadataHandler.raise_exception()

        out: Iterable[str] = iter([])

        for _, backend in _registry.items():
            with contextlib.suppress(NotImplementedError):
                out = itertools.chain(backend(self._path).get_keys(), out)

        return out

    @staticmethod
    def raise_exception() -> NoReturn:
        """Raise an exception for a operations without implementation."""
        msg = f"{inspect.stack()[1][3]} has no implementation"
        _logger.warning(msg, once=True)
        raise UnsupportedMetadataOperation(msg)


class UnsupportedMetadataOperation(NotImplementedError):
    """Raised if for an Operations, no function implementation is registered."""


def register(plugin: Type[MetadataPlugin]) -> None:
    """Decorator to register a function implementation.

    Args:
        operation: Operation for which the decorated function is registered.
    """
    assert plugin.name, "Required to have `plugin.name` set"
    assert plugin.version, "Required to have `plugin.version` set"

    _logger.debug(f"Registring metadata plugin {plugin.name}")
    if plugin.name in _registry:
        _logger.warning(
            "Metadata plugin {name} has already been registered. Ignoring it."
        )
        return

    _registry[plugin.name] = plugin


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
