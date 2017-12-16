# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.config.keybindings."""

from vimiv.config import keybindings


def test_add_keybinding():
    @keybindings.add("t")
    def test():
        pass
    bindings = keybindings.get("global")
    assert ("t", "test") in bindings.items()


def test_add_keybinding_with_args():
    @keybindings.add("t", args=["--any"])
    def test():
        pass
    bindings = keybindings.get("global")
    assert ("t", "test --any") in bindings.items()
