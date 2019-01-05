# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
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
