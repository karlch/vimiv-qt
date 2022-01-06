# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.gui.statusbar."""

import pytest

from vimiv.gui import statusbar


@pytest.mark.parametrize(
    "text, expected",
    [
        (" ", " "),
        ("this is text", "this is text"),
        ("one  two", "one&nbsp;&nbsp;two"),
        ("one two  three  four five", "one two&nbsp;&nbsp;three&nbsp;&nbsp;four five"),
    ],
)
def test_escape_subsequent_space_for_html(text, expected):
    assert statusbar.StatusBar._escape_subsequent_space_for_html(text) == expected
