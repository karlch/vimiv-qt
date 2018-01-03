# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.misc."""

from vimiv.utils import misc


def test_add_html():
    assert misc.add_html("b", "hello") == "<b>hello</b>"


def test_strip_html():
    assert misc.strip_html("<b>hello</b>") == "hello"


def test_clamp_with_min_and_max():
    assert misc.clamp(2, 0, 5) == 2
    assert misc.clamp(2, 3, 5) == 3
    assert misc.clamp(2, 0, 1) == 1


def test_clamp_with_max():
    assert misc.clamp(2, None, 5) == 2
    assert misc.clamp(2, None, 1) == 1


def test_clamp_with_min():
    assert misc.clamp(2, 0, None) == 2
    assert misc.clamp(2, 3, None) == 3


def test_clamp_with_none():
    assert misc.clamp(2, None, None) == 2
