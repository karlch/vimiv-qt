# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

from contextlib import suppress

import pytest_bdd as bdd

import vimiv
from vimiv import api
from vimiv.commands import runners


bdd.scenarios("commandline.feature")


@bdd.when("I run help <topic>")
def run_help(topic):
    runners.run(f"help {topic}", mode=api.modes.current())


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
    with suppress(api.commands.CommandNotFound):
        command = api.commands.get(topic, mode=api.modes.current())
        assert command.description in message_widget.text()
        return
    with suppress(KeyError):
        setting = api.settings.get(topic)
        assert setting.desc in message_widget.text()
        return
    raise AssertionError(f"Topic '{topic}' not found")
