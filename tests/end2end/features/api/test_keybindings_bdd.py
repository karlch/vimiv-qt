# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("keybindings.feature")


@pytest.fixture(autouse=True)
def cleanup_keybindings():
    """Fixture to delete any keybindings that were created in this feature."""

    def copy_bindings():
        """Helper function to retrieve a 'deepcopy' of the current keybindings."""
        return {mode: dict(api.keybindings._registry[mode]) for mode in api.modes.ALL}

    init_bindings = copy_bindings()  # Store initial keybindings
    yield
    # Delete anything from keybindings that was not in the initial keybindings
    updated_bindings = copy_bindings()
    for mode, mode_bindings in updated_bindings.items():
        for binding in mode_bindings:
            if binding not in init_bindings[mode]:
                del api.keybindings._registry[mode][binding]


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
