# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Storage and getter function for keybindings.

Module Attributes:
    _registry: Dictionary storing the keybindings for each mode.
"""

import collections

from vimiv import modes


def add(keybinding, command, mode="global"):
    """Decorator to add a keybinding.

    Args:
        command: Command to bind to.
        keybinding: Key to bind.
        mode: Mode in which the keybinding is valid.
    """
    def decorator(function):
        _registry[mode][keybinding] = command
        def inside(*args, **kwargs):
            return function(*args, **kwargs)
        return inside
    return decorator


class Bindings(collections.UserDict):
    """Store keybindings of one mode.

    Essentially a simple python dictionary which is stored in the module
    attribute _registry at initialization so it can be accessed with the
    get(mode) function.
    """

    def __init__(self, startdict=None):
        super().__init__()
        if startdict:
            self.update(startdict)

    def __add__(self, other):
        return Bindings(startdict={**self, **other})

    def partial_match(self, keys):
        """Check if keys match some of the bindings partially.

        Args:
            keys: String containing the keynames to check, e.g. "g".
        Return:
            True for match.
        """
        if not keys:
            return False
        for binding in self:
            if binding.startswith(keys):
                return True
        return False


_registry = {mode: Bindings() for mode in modes.__names__}


def get(mode):
    """Return the keybindings of one specific mode."""
    if mode in ["image", "thumbnail", "library"]:
        return _registry[mode] + _registry["global"]
    return _registry[mode]


def items():
    return _registry.items()


def clear():
    """Clear all keybindings."""
    for bindings in _registry.values():
        bindings.clear()
