# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for commands.history.History."""

import json
import os

import pytest

from vimiv import api
from vimiv.commands.history import History


MODES = (*api.modes.GLOBALS, api.modes.MANIPULATE)
MAX_ITEMS = 20
MODE_HISTORY = {
    mode.name: [f":{mode.name}-{i:01d}" for i in range(MAX_ITEMS)] for mode in MODES
}
LEGACY_HISTORY = [f":command-{i:01d}" for i in range(MAX_ITEMS)]


@pytest.fixture()
def mode_based_history_file(tmp_path, mocker):
    """Fixture to create mode-based history file to initialize History."""
    path = tmp_path / "history.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(MODE_HISTORY, f)

    mocker.patch.object(History, "filename", return_value=str(path))


@pytest.fixture()
def legacy_history_file(tmp_path, mocker):
    """Fixture to create legacy file to initialize History."""
    path = tmp_path / "history"
    path.write_text("\n".join(LEGACY_HISTORY) + "\n")
    mocker.patch.object(History, "filename", return_value=str(path) + ".json")


@pytest.fixture()
def history():
    """Fixture to create a clean history object to test."""
    yield History(":", MAX_ITEMS)


def test_read_history(mode_based_history_file, history):
    for mode, history_deque in history.items():
        assert list(history_deque) == MODE_HISTORY[mode.name]


def test_write_history(mode_based_history_file, history):
    for mode, history_deque in history.items():
        history_deque.extend(MODE_HISTORY[mode.name])
    history.write()

    with open(history.filename(), "r", encoding="utf-8") as f:
        written_history = json.load(f)

    assert written_history == MODE_HISTORY


def test_migrate_history(legacy_history_file, history):
    # Correctly read into new mode - deque - structure
    assert [mode.name for mode in history] == list(MODE_HISTORY.keys())
    for history_deque in history.values():
        assert list(history_deque) == LEGACY_HISTORY
    # Backup created
    assert os.path.isfile(history.filename().replace(".json", ".bak"))
