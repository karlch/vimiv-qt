# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Custom data types."""

import enum
import typing

from vimiv import checkversion


AnyT = typing.TypeVar("AnyT")
FuncT = typing.TypeVar("FuncT", bound=typing.Callable[..., typing.Any])
FuncNoneT = typing.TypeVar("FuncNoneT", bound=typing.Callable[..., None])
NumberT = typing.TypeVar("NumberT", int, float)

Number = typing.Union[int, float]
NumberStr = typing.Union[Number, str]
IntStr = typing.Union[int, str]


@enum.unique
class Exit(enum.IntEnum):
    """Enum class for the different integer exit codes."""

    success = 0
    err_exception = 1  # Uncaught exception
    err_version = checkversion.ERR_CODE  # Unsupported dependency version
    err_config = 3  # Critical error when parsing configuration files
    err_suicide = 42  # Forceful quit
    signal = 128  # Exit by signal + signum
