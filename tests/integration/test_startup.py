# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Test interaction between functions in vimiv.startup."""

import logging

from vimiv import startup
from vimiv.config import settings


def test_parse_geometry():
    parser = startup.get_argparser()
    args = parser.parse_args(["--geometry=200x200"])
    assert args.geometry == (200, 200)


def test_parse_log_level():
    parser = startup.get_argparser()
    args = parser.parse_args(["--log-level=Error"])
    assert args.log_level == logging.ERROR


def test_parse_setting():
    parser = startup.get_argparser()
    args = parser.parse_args(["--set", "statusbar.show", "no"])
    assert args.cmd_settings == [["statusbar.show", "no"]]


def test_update_setting_from_cmdline():
    settings.init_defaults()
    parser = startup.get_argparser()
    args = parser.parse_args(["--set", "statusbar.show", "no"])
    startup.update_settings(args)
    assert settings.get_value("statusbar.show") is False
