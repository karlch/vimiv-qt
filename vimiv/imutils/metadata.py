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

from enum import Enum
import itertools
import inspect
from typing import Dict, Tuple, NoReturn, Sequence, Iterable, Callable

from vimiv.utils import log, customtypes

_logger = log.module_logger(__name__)

# Type returned by `MetadataHandler.get_metadata`. Key if dictionary is the metadata
# key. Value is a tuple of name and value for that key.
MetadataDictT = Dict[str, Tuple[str, str]]


class Operations(str, Enum):
    """Represents all possible function clients can implement."""

    # TODO: From 3.11 on use StrEnum and auto()
    copy_metadata = "copy_metadata"
    get_date_time = "get_date_time"
    get_metadata = "get_metadata"
    get_keys = "get_keys"


class _MetadataRegistry(dict):
    """Handles the registration of function implementations.

    Values:
        Operations.copy_metadata: List of functions
        Operations.get_date_time: Function
        Operations.get_metadata: List of functions
        Operations.get_keys: List of functions
    """

    def __init__(self):
        super().__init__()
        _logger.debug("Initializing metadata registry")
        self[Operations.copy_metadata] = []
        self[Operations.get_date_time] = None
        self[Operations.get_metadata] = []
        self[Operations.get_keys] = []

    def register(self, operation: Operations, func: customtypes.FuncT) -> None:
        """Registers a function implementation for a specific method.

        With the exception of `Operations.get_date_time`, multiple implementation
        can be registered for a single method. For `Operations.get_date_time`,
        consecutive calls to this function overwrite the previously stored
        function.

        Args:
            operation: Operation for which the function is registered.
            func: Function to be registered.
        """

        if operation == Operations.get_date_time:
            if self[operation]:
                _logger.warning(
                    f"{Operations.get_date_time} has already an implementation."
                    "Overwriting it."
                )
            self[operation] = func
        else:
            self[operation].append(func)

        _logger.debug(f"Registered {func.__name__} for {operation}")


_registry = _MetadataRegistry()


def has_copy_metadata() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `copy_metadata`."""
    return bool(_registry[Operations.copy_metadata])


def has_get_date_time() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `get_date_time`."""
    return bool(_registry[Operations.get_date_time])


def has_get_metadata() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `get_metadata`."""
    return bool(_registry[Operations.get_metadata])


def has_get_keys() -> bool:
    """Return True iff `MetadataHandler` has an implementation for `get_keys`."""
    return bool(_registry[Operations.get_keys])


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

        failed = False

        for f in _registry[Operations.copy_metadata]:
            try:
                out = f(self._path, dest, reset_orientation)
            except TypeError:
                out = f(self._path, dest)

            if not out:
                failed = True

        if failed:
            _logger.warning(
                "Some implementations failed while copying metadata."
                "Some metadata may be missing in the destination image."
            )

    def get_date_time(self) -> str:
        """Get creation date and time as formatted string."""

        if not has_get_date_time():
            MetadataHandler.raise_exception()

        return _registry[Operations.get_date_time](self._path)

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

        for f in _registry[Operations.get_metadata]:
            # TODO: from 3.9 on use: out = out | f(self.path, keys)
            out = {**f(self._path, keys), **out}

        return out

    def get_keys(self) -> Iterable[str]:
        """Retrieve the key of all metadata values available in the current image."""

        if not has_get_keys():
            MetadataHandler.raise_exception()

        out: Iterable[str] = iter([])

        for f in _registry[Operations.get_keys]:
            out = itertools.chain(f(self._path), out)

        return out

    @staticmethod
    def raise_exception() -> NoReturn:
        """Raise an exception for a operations without implementation."""
        msg = f"{inspect.stack()[1][3]} has no implementation"
        _logger.warning(msg, once=True)
        raise UnsupportedMetadataOperation(msg)


class UnsupportedMetadataOperation(NotImplementedError):
    """Raised if for an Operations, no function implementation is registered."""


def register(operation: Operations) -> Callable[[customtypes.FuncT], customtypes.FuncT]:
    """Decorator to register a function implementation.

    Args:
        operation: Operation for which the decorated function is registered.
    """

    def decorator(func: customtypes.FuncT) -> customtypes.FuncT:
        _registry.register(operation, func)
        return func

    return decorator


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
