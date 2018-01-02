# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.


import pytest

from vimiv.config import styles


@pytest.fixture
def new_style():
    new_style = styles.Style("new_style")
    yield new_style
    del new_style


def test_add_style_option(new_style):
    new_style["red"] = "#ff0000"
    assert new_style["{red}"] == "#ff0000"


def test_fail_add_non_string_style_option(new_style):
    with pytest.raises(AssertionError, match="must be string"):
        new_style[True] = "#ff0000"


def test_fail_add_non_string_style_value(new_style):
    with pytest.raises(AssertionError, match="must be string"):
        new_style["red"] = 12


def test_replace_referenced_variables(mocker, new_style):
    mocker.patch.object(styles, "get_current", return_value=new_style)
    new_style["red"] = "#ff0000"
    new_style["error.fg"] = "{red}"
    styles.replace_referenced_variables()
    assert new_style["{error.fg}"] == "#ff0000"
