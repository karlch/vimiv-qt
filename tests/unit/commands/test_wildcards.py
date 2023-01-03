# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.wildcards."""

import shlex
import string

import pytest

from vimiv.commands import wildcards


@pytest.mark.parametrize("wildcard", ("%", "%m", "%wildcard", "%f"))
@pytest.mark.parametrize("escaped", (True, False))
@pytest.mark.parametrize(
    "text", ("{wildcard} start", "in the {wildcard} middle", "end {wildcard}")
)
def test_expand_wildcard(wildcard, escaped, text):
    text = text.format(wildcard=rf"\{wildcard}" if escaped else wildcard)
    paths = "this", "is", "text"
    result = wildcards.expand(text, wildcard, lambda: paths)

    if escaped:
        expected = text.replace("\\", "")
    else:
        expected = text.replace(wildcard, " ".join(paths))

    assert result == expected


@pytest.mark.parametrize("char", string.ascii_letters)
@pytest.mark.parametrize("wildcard", ("%",))
def test_expand_with_backslash(wildcard, char):
    paths = (rf"\{char}",)
    expected = " ".join(shlex.quote(path) for path in paths)

    result = wildcards.expand(wildcard, wildcard, lambda: paths)
    assert result == expected


def test_recursive_wildcards():
    """Ensure unescaping of wildcards does not lead to them being matched later."""
    text = r"This has an escaped wildcard \%m"
    expected = "This has an escaped wildcard %m"
    intermediate = wildcards.expand(text, "%m", lambda: "anything")
    result = wildcards.expand(intermediate, "%", lambda: "anything")
    assert result == expected


@pytest.mark.parametrize("path", (r"\.jpg", "spaced path.jpg", r"\%.jpg"))
def test_escape_path(path: str):
    expected = "'" + path.replace("\\", "\\\\").replace("%", "\\%") + "'"
    assert wildcards.escape_path(path) == expected
