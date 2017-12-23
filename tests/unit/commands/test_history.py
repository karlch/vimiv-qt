# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for commands.history."""

from vimiv.commands import history


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
    first = hist.cycle("next", "temporary")
    assert first == "first"
    second = hist.cycle("next", "")
    assert second == "second"
    first = hist.cycle("prev", "")
    assert first == "first"
    temporary = hist.cycle("prev", "")
    assert temporary == "temporary"


def test_do_not_fail_cycle_on_empty_history():
    hist = history.History([])
    result = hist.cycle("next", "temporary")
    assert result == ""


def test_clear_temporary_history_element():
    hist = history.History(["first"])
    hist.cycle("next", "temporary")
    hist.update("second")
    assert "temporary" not in hist
