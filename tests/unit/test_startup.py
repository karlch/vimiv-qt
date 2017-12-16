# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.startup."""

import logging
import os

from vimiv import startup


def test_parser_prog_name():
    parser = startup.get_argparser()
    assert parser.prog == "vimiv"


def test_parser_description():
    parser = startup.get_argparser()
    assert "image viewer" in parser.description


def test_init_paths_with_images(mocker):
    mocker.patch("vimiv.utils.files.get_supported",
                 return_value=(["dir/image.jpg"], []))
    mocker.patch("os.chdir")
    assert startup.init_paths(["any"]) == ["dir/image.jpg"]
    os.chdir.assert_called_once_with(os.path.abspath("dir"))


def test_init_paths_with_directory(mocker):
    mocker.patch("vimiv.utils.files.get_supported",
                 return_value=([], ["dir"]))
    mocker.patch("os.chdir")
    assert startup.init_paths(["any"]) is None
    os.chdir.assert_called_once_with("dir")


def test_init_paths_with_both(mocker):
    mocker.patch("vimiv.utils.files.get_supported",
                 return_value=(["foo/bar.png"], ["dir"]))
    mocker.patch("os.chdir")
    mocker.patch("logging.warning")
    assert startup.init_paths(["any"]) == ["foo/bar.png"]
    os.chdir.assert_called_once_with(os.path.abspath("foo"))
    logging.warning.assert_called_once()


def test_init_paths_with_multiple_directories(mocker):
    mocker.patch("vimiv.utils.files.get_supported",
                 return_value=([], ["dir1", "dir2"]))
    mocker.patch("os.chdir")
    mocker.patch("logging.warning")
    assert startup.init_paths(["any"]) is None
    os.chdir.assert_called_once_with("dir1")
    logging.warning.assert_called_once()
