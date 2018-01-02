# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.startup."""

import os

from vimiv import startup


def test_parser_prog_name():
    parser = startup.get_argparser()
    assert parser.prog == "vimiv"


def test_parser_description():
    parser = startup.get_argparser()
    assert "image viewer" in parser.description


def test_init_directories(mocker):
    mocker.patch("os.path.isdir", return_value=False)
    mocker.patch("os.mkdir")
    mocker.patch("vimiv.utils.xdg.get_vimiv_cache_dir", return_value="cache")
    mocker.patch("vimiv.utils.xdg.get_vimiv_config_dir", return_value="config")
    mocker.patch("vimiv.utils.xdg.get_vimiv_data_dir", return_value="data")
    startup.init_directories()
    # Check if all directories were created
    os.mkdir.assert_any_call("cache")
    os.mkdir.assert_any_call("config")
    os.mkdir.assert_any_call("data")
    os.mkdir.assert_any_call("config/styles")
