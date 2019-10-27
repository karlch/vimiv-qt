# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.runners."""

import pytest

from vimiv import api
from vimiv.commands import runners


PERCENT_TEXT = "expected"
PERCENT_M_LIST = ["mark1", "mark2", "mark3"]


@pytest.fixture(autouse=True)
def mock_percents(mocker):
    """Fixture to mock objects sending % and %m."""
    mocker.patch.object(api, "current_path", return_value=PERCENT_TEXT)
    mock_mark = mocker.patch.object(api, "mark")
    type(mock_mark).paths = mocker.PropertyMock(return_value=PERCENT_M_LIST)


@pytest.mark.parametrize("text", [" ", "\n", " \n", "\t\t", "\n \t"])
def test_text_non_whitespace_with_whitespace(text):
    """Ensure the decorated function is not called with plain whitespace."""

    @runners.text_non_whitespace
    def function(input):
        raise AssertionError("The function should not be called")

    function(text)


@pytest.mark.parametrize("text", [" txt", "\ntxt", " \ntxt", "\ttxt\t", "\n txt\t"])
def test_text_non_whitespace_with_non_whitespace(text, mocker):
    """Ensure the decorated function is called with stripped text."""

    mock = mocker.Mock()

    @runners.text_non_whitespace
    def function(input):
        mock(input)

    function(text)
    assert mock.called_once_with("txt")


def test_expand_percent():
    result = runners.expand_percent("command %", "any")
    expected = result.replace("%", PERCENT_TEXT)
    assert result == expected


def test_expand_marked():
    result = runners.expand_percent("command %m", "any")
    expected = result.replace("%m", " ".join(PERCENT_M_LIST))
    assert result == expected


@pytest.mark.parametrize("wildcard", ("%", "%m"))
def test_do_not_expand_escaped_wildcard(wildcard):
    result = runners.expand_percent(f"command \\{wildcard}", "any")
    expected = result.replace("\\", "")
    assert result == expected
