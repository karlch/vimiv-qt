# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.utils.misc."""

from vimiv.utils import misc


def test_add_html():
    assert misc.add_html("b", "hello") == "<b>hello</b>"


def test_strip_html():
    assert misc.strip_html("<b>hello</b>") == "hello"


def test_clamp_with_min_and_max():
    assert misc.clamp(2, 5, 0) == 2
    assert misc.clamp(2, 5, 3) == 3
    assert misc.clamp(2, 1, 0) == 1


def test_clamp_with_max():
    assert misc.clamp(2, 5, None) == 2
    assert misc.clamp(2, 1, None) == 1


def test_clamp_with_min():
    assert misc.clamp(2, None, 0) == 2
    assert misc.clamp(2, None, 3) == 3


def test_clamp_with_none():
    assert misc.clamp(2, None, None) == 2
