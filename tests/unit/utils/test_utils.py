# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils"""

from vimiv import utils


def test_ignore_single_exception():
    with utils.ignore(ValueError):
        int("32")


def test_ignore_multiple_exceptions():
    with utils.ignore(ValueError, IndexError):
        int("32")
        [][1]


def test_add_html():
    assert utils.add_html("b", "hello") == "<b>hello</b>"


def test_strip_html():
    assert utils.strip_html("<b>hello</b>") == "hello"


def test_clamp_with_min_and_max():
    assert utils.clamp(2, 0, 5) == 2
    assert utils.clamp(2, 3, 5) == 3
    assert utils.clamp(2, 0, 1) == 1


def test_clamp_with_max():
    assert utils.clamp(2, None, 5) == 2
    assert utils.clamp(2, None, 1) == 1


def test_clamp_with_min():
    assert utils.clamp(2, 0, None) == 2
    assert utils.clamp(2, 3, None) == 3


def test_clamp_with_none():
    assert utils.clamp(2, None, None) == 2
