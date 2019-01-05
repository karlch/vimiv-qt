# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for functions in vimiv.commands.argtypes."""

import argparse
import logging

import pytest

from vimiv.commands import argtypes


def test_positive_float():
    text = "2.2"
    parsed_value = argtypes.positive_float(text)
    assert parsed_value == 2.2


def test_fail_positive_float():
    with pytest.raises(ValueError, match="could not convert"):
        argtypes.positive_float("foo")
    with pytest.raises(argparse.ArgumentTypeError, match="must be positive"):
        argtypes.positive_float(-1)


def test_geometry():
    text = "300x500"
    parsed_value = argtypes.geometry(text)
    assert parsed_value == (300, 500)


def test_fail_geometry():
    with pytest.raises(ValueError, match="invalid"):
        argtypes.geometry("a xylophone")
    with pytest.raises(ValueError, match="invalid"):
        argtypes.geometry("200xbar")
    with pytest.raises(ValueError, match="invalid"):
        argtypes.geometry("12xfoo")
    with pytest.raises(argparse.ArgumentTypeError, match="form WIDTHxHEIGHT"):
        argtypes.geometry("1000")
    with pytest.raises(argparse.ArgumentTypeError, match="must be positive"):
        argtypes.geometry("-100x200")


def test_existing_file(mocker):
    mocker.patch("os.path.isfile", return_value=True)
    assert "any" == argtypes.existing_file("any")


def test_fail_existing_file(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    with pytest.raises(argparse.ArgumentTypeError, match="No file called"):
        argtypes.existing_file("any")


def test_existing_path(mocker):
    mocker.patch("os.path.exists", return_value=True)
    assert "any" == argtypes.existing_path("any")


def test_fail_existing_path(mocker):
    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(argparse.ArgumentTypeError, match="No path called"):
        argtypes.existing_path("any")


def test_scroll_direction():
    directions = ["left", "right", "up", "down"]
    for d in directions:
        assert d == argtypes.scroll_direction(d)


def test_fail_scroll_direction():
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid scroll"):
        argtypes.scroll_direction("other")


def test_zoom():
    zooms = ["in", "out"]
    for z in zooms:
        assert z == argtypes.zoom(z)


def test_fail_zoom():
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid zoom"):
        argtypes.zoom("other")


def test_log_level():
    level_dict = {"critical": logging.CRITICAL,
                  "error": logging.ERROR,
                  "warning": logging.WARNING,
                  "info": logging.INFO,
                  "debug": logging.DEBUG}
    for name, level in level_dict.items():
        assert argtypes.loglevel(name) == level


def test_fail_log_level():
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid loglevel"):
        argtypes.loglevel("other")


def test_image_scale_text():
    scales = ["fit", "fit-width", "fit-height"]
    for scale in scales:
        assert argtypes.image_scale(scale) == scale


def test_image_scale_float(mocker):
    mocker.patch.object(argtypes, "positive_float")
    argtypes.image_scale("0.5")
    argtypes.positive_float.assert_called_once_with("0.5")


def test_widget():
    widgets = ["library"]
    for w in widgets:
        assert w == argtypes.widget(w)


def test_fail_widget():
    with pytest.raises(argparse.ArgumentTypeError, match="No widget"):
        argtypes.widget("browser")


def test_command_history_direction():
    directions = ["next", "prev"]
    for d in directions:
        assert d == argtypes.command_history_direction(d)


def test_fail_command_history_direction():
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid history"):
        argtypes.command_history_direction("other")
