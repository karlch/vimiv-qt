# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import contextlib

import pytest
import pytest_bdd as bdd

import vimiv
from vimiv import api
from vimiv.commands import runners


bdd.scenarios("commandline.feature")


@pytest.fixture()
def history(commandline):
    """Fixture to retrieve the commandline history object."""
    return commandline._history


@bdd.when("I run help <topic>")
def run_help(topic):
    runners.run(f"help {topic}", mode=api.modes.current())


@bdd.when("I populate the history")
def populate_history(history):
    commands = [f":random-command{i:02d}" for i in range(20)]
    for historydeque in history.values():
        historydeque.extend(commands)


@bdd.then("the mode should not be command")
def check_commandline_closed():
    assert api.modes.current() != api.modes.COMMAND


@bdd.then(bdd.parsers.parse("the help for '{topic}' should be displayed"))
@bdd.then("the help for '<topic>' should be displayed")
def check_help(message_widget, topic):
    if topic == "vimiv":
        assert vimiv.__description__ in message_widget.text()
        return
    if topic == "wildcards":
        assert "wildcards" in message_widget.text().lower()
        return
    topic = topic.lower().lstrip(":")
    with contextlib.suppress(api.commands.CommandNotFound):
        command = api.commands.get(topic, mode=api.modes.current())
        assert command.description in message_widget.text()
        return
    with contextlib.suppress(KeyError):
        setting = api.settings.get(topic)
        assert setting.desc in message_widget.text()
        return
    raise AssertionError(f"Topic '{topic}' not found")


@bdd.then("the history of all modes should be empty")
def check_complete_history_empty(history):
    for historydeque in history.values():
        assert not historydeque


@bdd.then(bdd.parsers.parse("the history of {modename} mode should be empty"))
def check_mode_history_empty(history, modename):
    assert not history[api.modes.get_by_name(modename)]


@bdd.then(bdd.parsers.parse("the history of {modename} mode should not be empty"))
def check_mode_history_not_empty(history, modename):
    assert history[api.modes.get_by_name(modename)]
