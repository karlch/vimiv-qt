# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
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
    os.mkdir.assert_called_with("data")
