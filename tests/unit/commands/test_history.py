# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for commands.history."""

from vimiv.commands import history
from vimiv.commands.argtypes import HistoryDirection


def test_update_history():
    hist = history.History([])
    hist.update("test")
    assert "test" in hist


def test_update_history_with_duplicates():
    hist = history.History([])
    hist.update("test")
    hist.update("test")
    assert len(hist) == 1


def test_never_exceed_history_max_elements():
    hist = history.History([], 20)
    for i in range(25):
        hist.update("test-%d" % (i))
    assert len(hist) == 20


def test_cycle_through_history():
    hist = history.History(["first", "second", "third"])
    assert hist.cycle(HistoryDirection.Next, "temporary") == "first"
    assert hist.cycle(HistoryDirection.Next, "") == "second"
    assert hist.cycle(HistoryDirection.Prev, "") == "first"
    assert hist.cycle(HistoryDirection.Prev, "") == "temporary"


def test_do_not_fail_cycle_on_empty_history():
    hist = history.History([])
    result = hist.cycle(HistoryDirection.Next, "temporary")
    assert result == ""


def test_clear_temporary_history_element():
    hist = history.History(["first"])
    hist.cycle(HistoryDirection.Next, "temporary")
    hist.update("second")
    assert "temporary" not in hist


def test_substring_search_history():
    hist = history.History(["first", "final", "useless"])
    assert hist.substr_cycle(HistoryDirection.Next, "fi") == "first"
    assert hist.substr_cycle(HistoryDirection.Next, "fi") == "final"
    assert hist.substr_cycle(HistoryDirection.Next, "fi") == "fi"
    assert hist.substr_cycle(HistoryDirection.Prev, "fi") == "final"
