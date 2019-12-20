# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for commands.history.HistoryDeque."""

import pytest

import vimiv.commands.history
from vimiv.commands.argtypes import HistoryDirection


PREFIXES = ":?/"
CYCLE_HISTORY = [":first", ":second", ":third"]
SUBSTR_HISTORY = [":first", ":final", ":useless"]
MIXED_HISTORY = [prefix + text for text in ("first", "second") for prefix in PREFIXES]


@pytest.fixture()
def history_deque():
    yield vimiv.commands.history.HistoryDeque(PREFIXES, [], max_items=20)


@pytest.fixture()
def cycle_history_deque():
    yield vimiv.commands.history.HistoryDeque(PREFIXES, CYCLE_HISTORY, max_items=20)


@pytest.fixture()
def substr_history_deque():
    yield vimiv.commands.history.HistoryDeque(PREFIXES, SUBSTR_HISTORY, max_items=20)


@pytest.fixture()
def mixed_history_deque():
    yield vimiv.commands.history.HistoryDeque(PREFIXES, MIXED_HISTORY, max_items=20)


def test_update_history_deque(history_deque):
    history_deque.update(":test")
    assert ":test" in history_deque


def test_fail_update_history_invalid_prefix(history_deque):
    with pytest.raises(ValueError):
        history_deque.update("test")


def test_fail_update_history_empty_command(history_deque):
    with pytest.raises(ValueError):
        history_deque.update("")


def test_update_history_with_duplicates(history_deque):
    for _ in range(3):
        history_deque.update(":test")
    assert len(history_deque) == 1


def test_never_exceed_history_max_elements(history_deque):
    for i in range(history_deque.maxlen + 5):
        history_deque.update(":test-%d" % (i))
    assert len(history_deque) == history_deque.maxlen


def test_do_not_fail_cycle_on_empty_history(history_deque):
    expected = ":temporary"
    result = history_deque.cycle(HistoryDirection.Next, expected)
    assert result == expected


def test_do_not_store_temporary_history_element(history_deque):
    history_deque.cycle(HistoryDirection.Next, ":temporary")
    assert ":temporary" not in history_deque


def test_cycle_through_history(cycle_history_deque):
    start = ":start"
    for expected in CYCLE_HISTORY:
        assert cycle_history_deque.cycle(HistoryDirection.Next, start) == expected
    assert cycle_history_deque.cycle(HistoryDirection.Next, start) == start


def test_cycle_reverse_through_history(cycle_history_deque):
    start = ":start"
    for expected in CYCLE_HISTORY[::-1]:
        assert cycle_history_deque.cycle(HistoryDirection.Prev, start) == expected
    assert cycle_history_deque.cycle(HistoryDirection.Prev, start) == start


def test_substr_search_history(substr_history_deque):
    start = SUBSTR_HISTORY[0][:2]
    matches = [elem for elem in SUBSTR_HISTORY if elem.startswith(start)]
    for expected in matches:
        match = substr_history_deque.substr_cycle(HistoryDirection.Next, start)
        assert match == expected
    assert substr_history_deque.substr_cycle(HistoryDirection.Next, start) == start


@pytest.mark.parametrize("prefix", PREFIXES)
def test_do_not_mix_prefixes(mixed_history_deque, prefix):
    start = prefix + "start"
    matches = [elem for elem in MIXED_HISTORY if elem.startswith(prefix)]
    for expected in matches:
        assert mixed_history_deque.cycle(HistoryDirection.Next, start) == expected
    assert mixed_history_deque.substr_cycle(HistoryDirection.Next, start) == start


def test_reset_when_cycle_mode_changed(substr_history_deque):
    start = SUBSTR_HISTORY[0][:2]
    for expected in SUBSTR_HISTORY[:2]:
        match = substr_history_deque.substr_cycle(HistoryDirection.Next, start)
        assert match == expected
    expected = SUBSTR_HISTORY[-1]
    assert substr_history_deque.cycle(HistoryDirection.Prev, start) == expected
