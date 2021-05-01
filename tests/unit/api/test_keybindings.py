# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.keybindings."""

import pytest

from vimiv import api


@pytest.fixture(autouse=True)
def reset_to_default(cleanup_helper):
    """Fixture to ensure everything is reset to default after testing."""
    yield from cleanup_helper(api.keybindings._registry)
    api.settings.reset()


@pytest.mark.parametrize("binding, command", [("t1", "test"), (("t1", "t2"), "test")])
def test_add_keybindings(binding, command):
    @api.keybindings.register(binding, command, mode=api.modes.IMAGE)
    def test():
        """Nop function to register a keybinding."""

    bindings = api.keybindings.get(api.modes.IMAGE)
    for keysequence in binding if isinstance(binding, tuple) else (binding,):
        assert bindings[keysequence].value == command


def test_bind_unbind_keybinding():
    binding, command = "t1", "test"
    api.keybindings.bind(binding, command, api.modes.IMAGE)
    bindings = api.keybindings.get(api.modes.IMAGE)
    assert bindings[binding].value == command
    api.keybindings.unbind(binding, api.modes.IMAGE)
    assert binding not in bindings


def test_partial_matches():
    bindings_dict = {"t1": "test", "t2": "test"}
    bindings = api.keybindings._BindingsTrie()
    bindings.update(**bindings_dict)
    match = bindings.match("t")
    assert match.is_partial_match
    assert list(match.partial) == list(bindings_dict.items())


def test_partial_matches_with_special_keys():
    bindings_dict = {"<ctrl>a": "test", "<ctrl>b": "test"}
    bindings = api.keybindings._BindingsTrie()
    bindings.update(**bindings_dict)
    assert bindings.match("<").is_no_match
    match = bindings.match(("<ctrl>",))
    assert match.is_partial_match
    assert list(match.partial) == list(bindings_dict.items())


def test_partial_matches_with_multiple_special_keys():
    bindings_dict = {"<ctrl><alt>a": "test", "<ctrl><alt>b": "test"}
    bindings = api.keybindings._BindingsTrie()
    bindings.update(**bindings_dict)
    assert bindings.match("<").is_no_match
    assert bindings.match(("<ctrl>", "<")).is_no_match
    match = bindings.match(("<ctrl>", "<alt>"))
    assert match.is_partial_match
    assert list(match.partial) == list(bindings_dict.items())
