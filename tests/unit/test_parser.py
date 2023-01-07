# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for functions in vimiv.parser."""

import argparse
import logging
import os

import pytest

from vimiv.qt.core import QSize

from vimiv import parser


@pytest.fixture
def argparser():
    yield parser.get_argparser()


def test_parser_prog_name(argparser):
    assert argparser.prog == "vimiv"


def test_parser_description(argparser):
    assert "image viewer" in argparser.description


def test_geometry():
    text = "300x500"
    parsed_value = parser.geometry(text)
    assert parsed_value == QSize(300, 500)


def test_fail_geometry():
    with pytest.raises(ValueError, match="invalid"):
        parser.geometry("a xylophone")  # word with x to emulate form
    with pytest.raises(ValueError, match="invalid"):
        parser.geometry("200xnot_a_number")
    with pytest.raises(ValueError, match="invalid"):
        parser.geometry("12xnot_a_number")
    with pytest.raises(argparse.ArgumentTypeError, match="form WIDTHxHEIGHT"):
        parser.geometry("1000")
    with pytest.raises(argparse.ArgumentTypeError, match="must be positive"):
        parser.geometry("-100x200")


def test_existing_file(mocker):
    mocker.patch("os.path.isfile", return_value=True)
    assert os.path.abspath("any") == parser.existing_file("any")


def test_fail_existing_file(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    with pytest.raises(argparse.ArgumentTypeError, match="No file called"):
        parser.existing_file("any")


def test_existing_path(mocker):
    mocker.patch("os.path.exists", return_value=True)
    assert os.path.abspath("any") == parser.existing_path("any")


def test_fail_existing_path(mocker):
    mocker.patch("os.path.exists", return_value=False)
    with pytest.raises(argparse.ArgumentTypeError, match="No path called"):
        parser.existing_path("any")


def test_log_level():
    level_dict = {
        "critical": logging.CRITICAL,
        "error": logging.ERROR,
        "warning": logging.WARNING,
        "info": logging.INFO,
        "debug": logging.DEBUG,
    }
    for name, level in level_dict.items():
        assert parser.loglevel(name) == level


def test_fail_log_level():
    with pytest.raises(argparse.ArgumentTypeError, match="Invalid log level"):
        parser.loglevel("other")


def test_parse_settings(argparser):
    settings = [["statusbar.show", "false"], ["style", "default"]]
    arglist = []
    for name, value in settings:
        arglist.extend(("-s", name, value))
    args = argparser.parse_args(arglist)
    assert args.cmd_settings == settings


@pytest.mark.parametrize(
    "qtargs, expected",
    [
        ("--name floating", ["--name", "floating"]),
        ("--name floating --reverse", ["--name", "floating", "--reverse"]),
        ("--name 'has space'", ["--name", "has space"]),
    ],
)
def test_parse_qt_args(argparser, qtargs, expected):
    arglist = ["--qt-args", qtargs]
    args = argparser.parse_args(arglist)
    assert parser.get_qt_args(args) == expected
