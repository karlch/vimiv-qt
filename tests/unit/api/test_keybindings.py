# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.keybindings."""

# from vimiv.api import keybindings
# from vimiv.modes import Modes
from vimiv import api


def test_add_keybinding():
    @api.keybindings.register("t1", "test")
    def test():
        pass

    bindings = api.keybindings.get(api.modes.GLOBAL)
    assert ("t1", "test") in bindings.items()
    del bindings["t1"]


def test_add_multiple_keybindings():
    @api.keybindings.register(["t1", "t2"], "test")
    def test():
        pass

    bindings = api.keybindings.get(api.modes.GLOBAL)
    assert ("t1", "test") in bindings.items()
    assert ("t2", "test") in bindings.items()
    del bindings["t1"]
    del bindings["t2"]


def test_bind_unbind_keybinding():
    api.keybindings.bind("t2", "test", api.modes.IMAGE)
    assert ("t2", "test") in api.keybindings.get(api.modes.IMAGE).items()
    api.keybindings.unbind("t2", api.modes.IMAGE)
    assert ("t2", "test") not in api.keybindings.get(api.modes.IMAGE).items()
