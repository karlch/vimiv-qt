# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Module to store and expand wildcards.

Module Attributes:
    INTERNAL: List of all special vimiv-internal wildcards such as % or %m.
"""

import re
import shlex
import typing

from vimiv import api, utils

WildcardReturnT = typing.Union[str, typing.Iterable[str]]
WildcardCallbackT = typing.Callable[..., WildcardReturnT]


class Wildcard:
    """Storage class for a wildcard.

    Wildcards are called with the current mode to retrieve a single path or a list of
    paths the wildcard corresponds to. The current mode is required as many wildcards,
    such as the current path, are mode-dependent.

    Attributes:
        wildcard: String representing the wildcard, e.g. "%".
        description: Text describing what the wildcard gets expanded to.

        _callback: Function to call when expanding the wildcard.
    """

    def __init__(self, wildcard: str, description: str, callback: WildcardCallbackT):
        self.wildcard = wildcard
        self.description = description
        self._callback = callback

    def __call__(self, mode: api.modes.Mode) -> WildcardReturnT:
        return self._callback(mode)


INTERNAL = [
    Wildcard("%", "currently focused path or image", api.current_path),
    Wildcard("%f", "all paths in the current file list", api.pathlist),
    Wildcard("%m", "all marked paths", lambda _mode: api.mark.paths),
]


def expand_internal(text: str, mode: api.modes.Mode) -> str:
    """Expand all internal wildcards in text.

    Args:
        text: The command in which the wildcards are expanded.
        mode: Mode the command is run in to get correct path(-list).
    """
    for wildcard in INTERNAL:
        text = expand(text, wildcard.wildcard, wildcard, mode)
    return text


def expand(
    text: str, wildcard: str, callback: WildcardCallbackT, *args, **kwargs
) -> str:
    """Expand a wildcard in text to the shell escaped version of paths.

    The regular expression matches the wildcard in case it is not followed by any
    letters. This ensures correct handling of overlapping wildcards such as % and %m. In
    a first step the wildcard, if it is not escaped, is replaced by the paths. The
    second step removes the escape character in case the wildcard was escaped with a
    prepended backslash.

    The wildcard callback is expected to return a single path or a list of paths.

    Args:
        text: The command in which the wildcards are expanded.
        wildcard: The wildcard string to expand if not escaped.
        callback: Function called with args and kwargs to retrieve the wildcard value.
    """
    if wildcard in text:
        paths = callback(*args, **kwargs)
        paths = (paths,) if isinstance(paths, str) else paths
        quoted_paths = " ".join(shlex.quote(path) for path in paths)
        re_wildcard = f"{wildcard}([^a-zA-Z]|$)"
        text = re.sub(
            utils.RE_STR_NOT_ESCAPED + re_wildcard, rf"{quoted_paths}\1", text
        )
        text = re.sub(utils.RE_STR_ESCAPED + re_wildcard, rf"{wildcard}\1", text)
    return text