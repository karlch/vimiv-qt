# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.config.keybindings."""

from vimiv.config import keybindings


def test_add_keybinding():
    @keybindings.add("test", "t", "global")
    def test():
        pass
    bindings = keybindings.get("global")
    assert ("t", "test") in bindings.items()
