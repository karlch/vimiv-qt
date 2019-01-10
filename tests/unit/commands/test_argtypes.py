# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for types in vimiv.commands.argtypes."""

import pytest

from vimiv.commands import argtypes


def test_scroll_direction():
    # Would raise exception if a name is invalid
    [argtypes.Direction(name) for name in ["left", "right", "up", "down"]]


def test_fail_scroll_direction():
    with pytest.raises(ValueError, match="not a valid Direct"):
        argtypes.Direction("other")


def test_zoom():
    # Would raise exception if a name is invalid
    [argtypes.Zoom(name) for name in ["in", "out"]]


def test_fail_zoom():
    with pytest.raises(ValueError, match="not a valid Zoom"):
        argtypes.Zoom("other")


def test_image_scale_text():
    # Would raise exception if a name is invalid
    [argtypes.ImageScaleFloat(name)
        for name in ["fit", "fit-width", "fit-height"]]


def test_image_scale_float(mocker):
    assert argtypes.ImageScaleFloat("0.5") == 0.5


def test_command_history_direction():
    # Would raise exception if a name is invalid
    [argtypes.HistoryDirection(name) for name in ["next", "prev"]]


def test_fail_command_history_direction():
    with pytest.raises(ValueError, match="not a valid HistoryDirection"):
        argtypes.HistoryDirection("other")
