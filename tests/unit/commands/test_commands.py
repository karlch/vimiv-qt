# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands."""

import pytest

from vimiv import commands


@pytest.mark.parametrize(
    "number, count, max_count, expected",
    [
        (1, None, 5, 0),
        (1, 2, 5, 1),
        (10, None, 5, 4),
        (-1, None, 5, 4),
        (0, None, 5, 0),
    ],
)
def test_number_for_command(number, count, max_count, expected):
    assert commands.number_for_command(number, count, max_count=max_count) == expected


def test_fail_number_for_command():
    with pytest.raises(ValueError):
        commands.number_for_command(None, None, max_count=42)
