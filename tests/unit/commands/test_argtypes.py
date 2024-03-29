# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

"""Tests for types in vimiv.commands.argtypes."""

import pytest

from vimiv.commands import argtypes


@pytest.mark.parametrize("name", ("left", "right", "up", "down"))
def test_scroll_direction(name):
    # Would raise exception if a name is invalid
    assert isinstance(argtypes.Direction(name), argtypes.Direction)


def test_fail_scroll_direction():
    with pytest.raises(ValueError, match="not a valid Direct"):
        argtypes.Direction("other")


@pytest.mark.parametrize("name", ("in", "out"))
def test_zoom(name):
    # Would raise exception if a name is invalid
    assert isinstance(argtypes.Zoom(name), argtypes.Zoom)


def test_fail_zoom():
    with pytest.raises(ValueError, match="not a valid Zoom"):
        argtypes.Zoom("other")


@pytest.mark.parametrize("name", ("fit", "fit-width", "fit-height"))
def test_image_scale_text(name):
    # Would raise exception if a name is invalid
    assert isinstance(argtypes.ImageScaleFloat(name), argtypes.ImageScale)


def test_image_scale_float():
    assert argtypes.ImageScaleFloat("0.5") == 0.5


@pytest.mark.parametrize("name", ("next", "prev"))
def test_command_history_direction(name):
    # Would raise exception if a name is invalid
    assert isinstance(argtypes.HistoryDirection(name), argtypes.HistoryDirection)


def test_fail_command_history_direction():
    with pytest.raises(ValueError, match="not a valid HistoryDirection"):
        argtypes.HistoryDirection("other")


@pytest.mark.parametrize("size", ((3, 3), (4, 3), (16, 9)))
@pytest.mark.parametrize("separator", argtypes.AspectRatio.SEPARATORS)
def test_aspectratio(size, separator):
    definition = separator.join(str(length) for length in size)
    width, height = size
    aspectratio = argtypes.AspectRatio(definition)
    assert aspectratio.width() == int(width)
    assert aspectratio.height() == int(height)
    assert not aspectratio.keep


@pytest.mark.parametrize("definition", ("4to3", "4:3:2", "42", "hello:world"))
def test_fail_aspectratio(definition):
    with pytest.raises(ValueError, match="Invalid aspectratio"):
        argtypes.AspectRatio(definition)


@pytest.mark.parametrize("value", ("Keep", "keep", "keeP"))
def test_aspectratio_keep(value):
    aspectratio = argtypes.AspectRatio(value)
    assert aspectratio.keep
