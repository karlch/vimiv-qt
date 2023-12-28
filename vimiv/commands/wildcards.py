# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Module to store and expand wildcards.

Module Attributes:
    INTERNAL: List of all special vimiv-internal wildcards such as % or %m.
"""

import re
import shlex
import typing

from vimiv import api, utils

WildcardReturn = typing.Union[str, typing.Iterable[str]]
WildcardCallbackT = typing.Callable[..., WildcardReturn]


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

    def __call__(self, mode: api.modes.Mode) -> WildcardReturn:
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


def escape_path(path: str):
    """Escape path for wildcard expansion.

    Required to avoid crashes in the re module and properly treat paths that include
    wildcards in their name.

    See https://github.com/karlch/vimiv-qt/issues/218.
    """
    return shlex.quote(re.sub(r"([\\%\[\]\?\*])", r"\\\1", path))


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
        quoted_paths = " ".join(escape_path(path) for path in paths)
        re_wildcard = f"{wildcard}([^a-zA-Z]|$)"
        text = re.sub(
            utils.RE_STR_NOT_ESCAPED + re_wildcard, rf"{quoted_paths}\1", text
        )
        text = re.sub(utils.RE_STR_ESCAPED + re_wildcard, rf"{wildcard}\1", text)
    return text
