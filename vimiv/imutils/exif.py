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
from enum import Enum
import functools
import itertools
import inspect
from typing import Any, Dict, Tuple, NoReturn, Sequence, Iterable, Callable, List, Union

from vimiv.utils import log, lazy, is_hex, customtypes

_logger = log.module_logger(__name__)

ExifDictT = Dict[Any, Tuple[str, str]]


class Methods(str, Enum):
    """Represents all possible function clients can implement."""
    # TODO: From 3.11 on use StrEnum and auto()
    copy_metadata = "copy_metadata"
    get_date_time = "get_date_time"
    get_raw_metadata = "get_raw_metadata"
    get_formatted_metadata = "get_formatted_metadata"
    get_keys = "get_keys"


class _MetadataRegistry(dict):

    def __init__(self):
        super().__init__()
        _logger.debug("Initializing metadata registry")

        # TODO: use List[customtypes.FuncNoneT]
        # TODO: specific return type
        self[Methods.copy_metadata] = []  #: List[Callable[..., None]] = []
        self[Methods.get_date_time] = None  #: Union[Callable[..., str], None] = None
        self[Methods.get_raw_metadata] = []  #: List[Callable[..., ExifDictT]] = []
        self[Methods.get_formatted_metadata] = []  #: List[Callable[..., ExifDictT]] = []
        self[Methods.get_keys] = []  #: List[Callable[..., Any]] = []

    def register(self, method: Methods, func: customtypes.FuncT) -> None:
        """Registers a func for a specific method."""

        if method == Methods.get_date_time:
            if self[method] is not None:
                _logger.warning(f"Key {Methods.get_date_time} has already been set. Overwriting old implementation with new one.")
            self[method] = func
        else:
            self[method].append(func)

        _logger.debug(f"Registered {func.__name__} for {method}")


_registry = _MetadataRegistry()


class MetadataHandler:
    """ """

    def __init__(self, path: str):
        self.path = path

    def copy_metadata(self, dest: str, reset_orientation: bool = True) -> None:
        """Copy exif information from current image to dest.

        Args:
            dest: Path to write the exif information to.
            reset_orientation: If true, reset the exif orientation tag to normal.
        """

        if len(_registry[Methods.copy_metadata]) == 0:
            MetadataHandler.raise_exception()

        for f in _registry[Methods.copy_metadata]:
            f(self.path, dest, reset_orientation)

    def get_date_time(self) -> str:
        """Get exif creation date and time as formatted string."""

        if _registry[Methods.get_date_time] is None:
            MetadataHandler.raise_exception()

        return _registry[Methods.get_date_time](self.path)

    def get_raw_metadata(self, desired_keys: Sequence[str]) -> ExifDictT:
        """Get a dictionary of metadata values."""

        if len(_registry[Methods.get_raw_metadata]) == 0:
            MetadataHandler.raise_exception()

        out: ExifDictT = {}

        for f in _registry[Methods.get_raw_metadata]:
            # TODO: from 3.9 on use: out = out | f(self.path, desired_keys)
            out = {**out, **f(self.path, desired_keys)}

        return out

    def get_formatted_metadata(self, desired_keys: Sequence[str]) -> ExifDictT:
        """Get a dictionary of formatted metadata values."""

        if len(_registry[Methods.get_formatted_metadata]) == 0:
            MetadataHandler.raise_exception()

        out: ExifDictT = {}

        for f in _registry[Methods.get_formatted_metadata]:
            # TODO: from 3.9 on use: out = out | f(self.path, desired_keys)
            out = {**out, **f(self.path, desired_keys)}

        return out

    def get_keys(self) -> Iterable[str]:
        """Retrieve the name of all exif keys available."""

        if len(_registry[Methods.get_keys]) == 0:
            MetadataHandler.raise_exception()

        out: Iterable[str] = iter([])

        for f in _registry[Methods.get_keys]:
            out = itertools.chain(f(self.path), out)

        return out

    @staticmethod
    def raise_exception() -> NoReturn:
        """Raise an exception for a operations without implementation."""
        msg = f"{inspect.stack()[1][3]} has no implementation"
        _logger.warning(msg, once=True)
        raise UnsupportedMetadataOperation(msg)


class UnsupportedMetadataOperation(NotImplementedError):
    """Raised if an metadata operation is not supported by any loaded backend."""


def register(method: Methods) -> Callable[[customtypes.FuncT], customtypes.FuncT]:

    def decorator(func: customtypes.FuncT) -> customtypes.FuncT:
        _registry.register(method, func)
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
