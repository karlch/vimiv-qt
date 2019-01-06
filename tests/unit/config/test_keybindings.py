# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.config.keybindings."""

from vimiv.config import keybindings
from vimiv.modes import Modes


def test_add_keybinding():
    @keybindings.add("t1", "test")
    def test():
        pass
    bindings = keybindings.get(Modes.GLOBAL)
    assert ("t1", "test") in bindings.items()


def test_bind_unbind_keybinding():
    keybindings.bind("t2", "test", Modes.IMAGE)
    assert ("t2", "test") in keybindings.get(Modes.IMAGE).items()
    keybindings.unbind("t2", Modes.IMAGE)
    assert ("t2", "test") not in keybindings.get(Modes.IMAGE).items()
