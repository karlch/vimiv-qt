# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for commands.history."""

import pytest

import vimiv.commands.history
from vimiv.commands.argtypes import HistoryDirection


PREFIXES = ":?/"
CYCLE_HISTORY = [":first", ":second", ":third"]
SUBSTR_HISTORY = [":first", ":final", ":useless"]
MIXED_HISTORY = [prefix + text for text in ("first", "second") for prefix in PREFIXES]


@pytest.fixture()
def history():
    yield vimiv.commands.history.History(PREFIXES, [], max_items=20)


@pytest.fixture()
def cycle_history():
    yield vimiv.commands.history.History(PREFIXES, CYCLE_HISTORY, max_items=20)


@pytest.fixture()
def substr_history():
    yield vimiv.commands.history.History(PREFIXES, SUBSTR_HISTORY, max_items=20)


@pytest.fixture()
def mixed_history():
    yield vimiv.commands.history.History(PREFIXES, MIXED_HISTORY, max_items=20)


def test_update_history(history):
    history.update(":test")
    assert ":test" in history


def test_fail_update_history_invalid_prefix(history):
    with pytest.raises(ValueError):
        history.update("test")


def test_fail_update_history_empty_command(history):
    with pytest.raises(ValueError):
        history.update("")


def test_update_history_with_duplicates(history):
    for _ in range(3):
        history.update(":test")
    assert len(history) == 1


def test_never_exceed_history_max_elements(history):
    for i in range(history.maxlen + 5):
        history.update(":test-%d" % (i))
    assert len(history) == history.maxlen


def test_do_not_fail_cycle_on_empty_history(history):
    expected = ":temporary"
    result = history.cycle(HistoryDirection.Next, expected)
    assert result == expected


def test_do_not_store_temporary_history_element(history):
    history.cycle(HistoryDirection.Next, ":temporary")
    assert ":temporary" not in history


def test_cycle_through_history(cycle_history):
    start = ":start"
    for expected in CYCLE_HISTORY:
        assert cycle_history.cycle(HistoryDirection.Next, start) == expected
    assert cycle_history.cycle(HistoryDirection.Next, start) == start


def test_cycle_reverse_through_history(cycle_history):
    start = ":start"
    for expected in CYCLE_HISTORY[::-1]:
        assert cycle_history.cycle(HistoryDirection.Prev, start) == expected
    assert cycle_history.cycle(HistoryDirection.Prev, start) == start


def test_substr_search_history(substr_history):
    start = SUBSTR_HISTORY[0][:2]
    matches = [elem for elem in SUBSTR_HISTORY if elem.startswith(start)]
    for expected in matches:
        assert substr_history.substr_cycle(HistoryDirection.Next, start) == expected
    assert substr_history.substr_cycle(HistoryDirection.Next, start) == start


@pytest.mark.parametrize("prefix", PREFIXES)
def test_do_not_mix_prefixes(mixed_history, prefix):
    start = prefix + "start"
    matches = [elem for elem in MIXED_HISTORY if elem.startswith(prefix)]
    for expected in matches:
        assert mixed_history.cycle(HistoryDirection.Next, start) == expected
    assert mixed_history.substr_cycle(HistoryDirection.Next, start) == start
