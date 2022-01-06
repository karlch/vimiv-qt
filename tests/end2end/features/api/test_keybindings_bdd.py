# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("keybindings.feature")


@pytest.fixture(autouse=True)
def cleanup_keybindings(cleanup_helper):
    """Fixture to delete any keybindings that were created during testing."""
    yield from cleanup_helper(api.keybindings._registry)


@bdd.then(bdd.parsers.parse("the keybinding {binding} should exist for mode {mode}"))
def keybinding_exists(binding, mode):
    mode = api.modes.get_by_name(mode)
    assert binding in api.keybindings._registry[mode]


@bdd.then(
    bdd.parsers.parse("the keybinding {binding} should not exist for mode {mode}")
)
def keybinding_not_exists(binding, mode):
    mode = api.modes.get_by_name(mode)
    assert binding not in api.keybindings._registry[mode]
