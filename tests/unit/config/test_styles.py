# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.


import pytest

from vimiv.config import styles


@pytest.fixture
def new_style():
    new_style = styles.create_default(save_to_file=False)
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
    new_style["red"] = "#ff0000"
    new_style["error.fg"] = "{red}"
    assert new_style["{error.fg}"] == "#ff0000"


def test_fail_get_nonexisting_style_option(mocker, new_style):
    styles._style = new_style
    assert styles.get("anything") == ""
    styles._style = None


def test_is_color_option():
    assert styles.Style.is_color_option("test.bg")
    assert styles.Style.is_color_option("test.fg")
    assert not styles.Style.is_color_option("test.fga")
    assert not styles.Style.is_color_option("test.f")


def test_check_valid_color():
    # If a check fails, ValueError is raised, so we need no assert statement
    styles.Style.check_valid_color("#fff")  # 3 digit hex
    styles.Style.check_valid_color("#FFF")  # 3 digit hex capital
    styles.Style.check_valid_color("#FfF")  # 3 digit hex mixed case
    styles.Style.check_valid_color("#0fF")  # 3 digit hex mixed case and number
    styles.Style.check_valid_color("#ffffff")  # 6 digit hex
    styles.Style.check_valid_color("#FFFFFF")  # 6 digit hex capital
    styles.Style.check_valid_color("#FFfFfF")  # 6 digit hex mixed case
    styles.Style.check_valid_color("#00fFfF")  # 6 digit hex mixed case and number


@pytest.mark.parametrize(
    "color",
    (
        "ffffff",  # Missing leading #
        "#fffffff",  # 7 digits
        "#fffff",  # 5 digits
        "#ffff",  # 4 digits
        "#ff",  # 2 digits
        "#f",  # 1 digit
        "#",  # 0 digits
        "#agfjkl",  # invalid content
    ),
)
def test_fail_check_valid_color(color):
    with pytest.raises(ValueError):
        styles.Style.check_valid_color(color)
