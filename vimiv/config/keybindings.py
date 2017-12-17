# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Storage and getter function for keybindings.

Module Attributes:
    _registry: Dictionary storing the keybindings for each mode.
"""

import collections


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

    def __add__(self, other):
        return {**self, **other}


_registry = {
    "global": Bindings(),
    "image": Bindings(),
    "library": Bindings(),
    "command": Bindings(),
}


def get(mode):
    """Return the keybindings of one specific mode."""
    if mode in ["image", "thumbnail", "library"]:
        return _registry[mode] + _registry["global"]
    return _registry[mode]


def items():
    return _registry.items()
