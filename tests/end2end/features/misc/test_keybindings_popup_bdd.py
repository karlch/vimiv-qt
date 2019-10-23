# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

import vimiv.gui.keybindings_popup
from vimiv import api, utils

bdd.scenarios("keybindings_popup.feature")


@pytest.fixture()
def keybindings_popup(mainwindow):
    """Fixture to retrieve the current keybindings pop-up."""
    for widget in mainwindow.children():
        if isinstance(widget, vimiv.gui.keybindings_popup.KeybindingsPopUp):
            return widget
    raise AssertionError("No keybindings pop-up open")


@bdd.when(bdd.parsers.parse("I type '{keys}' in the pop up"))
def press_keys_popup(keybindings_popup, qtbot, keys):
    qtbot.keyClicks(keybindings_popup._search, keys)


@bdd.then(bdd.parsers.parse("the keybindings pop up should contain '{text}'"))
def check_keybindings_popup_text(keybindings_popup, text):
    assert text in keybindings_popup.text


@bdd.then(bdd.parsers.parse("the keybindings pop up should describe '{command}'"))
def check_keybindings_popup_description(keybindings_popup, command):
    description = api.commands.get(command, api.modes.current()).description
    assert description in keybindings_popup.description


@bdd.then("the keybindings pop up description should be empty")
def check_keybindings_popup_description_empty(keybindings_popup):
    assert not keybindings_popup.description


@bdd.then(bdd.parsers.parse("'{search}' should be highlighted in '{command}'"))
def check_keybindings_popup_highlighting(keybindings_popup, search, command):
    highlight = keybindings_popup.highlighted_search_str(search)
    # Ensure the search_str is the actual highlighted string
    assert utils.strip_html(highlight) == search
    # Ensure the highlighted command is in the pop up text
    assert command.replace(search, highlight) in keybindings_popup.text
