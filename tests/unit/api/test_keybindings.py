# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.keybindings."""

from vimiv import api


def test_add_keybinding():
    @api.keybindings.register("t1", "test", mode=api.modes.IMAGE)
    def test():
        pass

    bindings = api.keybindings.get(api.modes.IMAGE)
    assert bindings["t1"].value == "test"
    del bindings["t1"]


def test_add_multiple_keybindings():
    @api.keybindings.register(("t1", "t2"), "test", mode=api.modes.IMAGE)
    def test():
        pass

    bindings = api.keybindings.get(api.modes.IMAGE)
    assert bindings["t1"].value == "test"
    assert bindings["t2"].value == "test"
    del bindings["t1"]
    del bindings["t2"]


def test_bind_unbind_keybinding():
    api.keybindings.bind("t2", "test", api.modes.IMAGE)
    bindings = api.keybindings.get(api.modes.IMAGE)
    assert bindings["t2"].value == "test"
    api.keybindings.unbind("t2", api.modes.IMAGE)
    assert "t2" not in bindings


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
