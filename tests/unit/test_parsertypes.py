# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for functions in vimiv.parsertypes."""

import argparse
import logging

import pytest

from vimiv import parsertypes


def test_positive_float():
    text = "2.2"
    parsed_value = parsertypes.positive_float(text)
    assert parsed_value == 2.2


def test_fail_positive_float():
    with pytest.raises(ValueError, match="could not convert"):
        parsertypes.positive_float("foo")
    with pytest.raises(argparse.ArgumentTypeError, match="must be positive"):
        parsertypes.positive_float(-1)


def test_geometry():
    text = "300x500"
    parsed_value = parsertypes.geometry(text)
    assert parsed_value == parsertypes.Geometry(300, 500)


def test_fail_geometry():
    with pytest.raises(ValueError, match="invalid"):
        parsertypes.geometry("a xylophone")
    with pytest.raises(ValueError, match="invalid"):
        parsertypes.geometry("200xbar")
    with pytest.raises(ValueError, match="invalid"):
        parsertypes.geometry("12xfoo")
    with pytest.raises(argparse.ArgumentTypeError, match="form WIDTHxHEIGHT"):
        parsertypes.geometry("1000")
    with pytest.raises(argparse.ArgumentTypeError, match="must be positive"):
        parsertypes.geometry("-100x200")


def test_existing_file(mocker):
    mocker.patch("os.path.isfile", return_value=True)
    assert "any" == parsertypes.existing_file("any")


def test_fail_existing_file(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    with pytest.raises(argparse.ArgumentTypeError, match="No file called"):
        parsertypes.existing_file("any")


def test_existing_path(mocker):
    mocker.patch("os.path.exists", return_value=True)
    assert "any" == parsertypes.existing_path("any")


def test_fail_existing_path(mocker):
    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(argparse.ArgumentTypeError, match="No path called"):
        parsertypes.existing_path("any")


def test_log_level():
    level_dict = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    for name, level in level_dict.items():
        assert parsertypes.loglevel(name) == level


def test_fail_log_level():
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid log level"):
        parsertypes.loglevel("other")
