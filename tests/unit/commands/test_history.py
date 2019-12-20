# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for commands.history.History."""

import os

import pytest

from vimiv import api
from vimiv.commands.history import History


MODES = (*api.modes.GLOBALS, api.modes.MANIPULATE)
MAX_ITEMS = 20
MODE_HISTORY = {
    mode: [f":{mode.name.lower()}-{i:01d}" for i in range(MAX_ITEMS)] for mode in MODES
}
LEGACY_HISTORY = [f":command-{i:01d}" for i in range(MAX_ITEMS)]


@pytest.fixture()
def mode_based_history_files(tmpdir, mocker):
    """Fixture to create mode-based history files to initialize History."""
    directory = tmpdir.mkdir("history")
    mocker.patch.object(History, "dirname", return_value=str(directory))
    for mode, commands in MODE_HISTORY.items():
        History._write(History.filename(mode), commands)


@pytest.fixture()
def legacy_history_file(tmpdir, mocker):
    """Fixture to create legacy file to initialize History."""
    path = tmpdir.join("history")
    path.write("\n".join(LEGACY_HISTORY) + "\n")
    mocker.patch.object(History, "dirname", return_value=str(path))


@pytest.fixture()
def history():
    """Fixture to create a clean history object to test."""
    yield History(":", MAX_ITEMS)


def test_read_history(mode_based_history_files, history):
    for mode, history_deque in history.items():
        assert list(history_deque) == MODE_HISTORY[mode]


def test_migrate_history(legacy_history_file, history):
    # Correctly read into new mode - deque - structure
    for mode, history_deque in history.items():
        assert list(history_deque) == LEGACY_HISTORY
    # Backup created
    assert os.path.isfile(history.dirname() + ".bak")
    # New structure saved
    history.write()
    for mode in MODE_HISTORY:
        assert os.path.isfile(history.filename(mode))
