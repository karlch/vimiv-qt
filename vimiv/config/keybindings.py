# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Storage and getter function for keybindings.

Module Attributes:
    _registry: Dictionary storing the keybindings for each mode.

//

Commands can be mapped to a sequence of keys using the utilities from the
``vimiv.config.keybindings`` module.

Adding a new default keybinding is done using the ``add`` decorator. This
decorator requires the sequence of keys to bind to as first argument, the
command as second argument and, similar to ``commands.register`` supports the
``mode`` keyword to define the mode in which the keybinding is valid.

As an example, let's bind the ``:hello-earth`` command from before to the key
sequence ``ge``::

    @keybindings.add("ge", "hello-earth")
    @commands.register()
    def hello_earth():
        print("hello earth")

If the keybinding requires passing any arguments to the command, these must be
passed as part of the command. For example, to great venus with ``gv`` and
earth with ``ge`` we could use::

    @keybindings.add("gv", "hello-planet --name=venus")
    @keybindings.add("ge", "hello-planet")
    @commands.argument("name", optional=True, default="earth")
    @commands.register()
    def hello_planet(name="earth"):
        print("hello", name)
"""

import collections

from vimiv.commands import cmdexc
from vimiv.modes import Modes


def add(keybinding, command, mode=Modes.GLOBAL):
    """Decorator to add a keybinding.

    Args:
        command: Command to bind to.
        keybinding: Key to bind.
        mode: Mode in which the keybinding is valid.
    """
    def decorator(function):
        bind(keybinding, command, mode)
        def inside(*args, **kwargs):
            return function(*args, **kwargs)
        return inside
    return decorator


def bind(keybinding, command, mode):
    """Store keybinding in registry.

    See config/configcommands.bind for the corresponding command.
    """
    _registry[mode][keybinding] = command


def unbind(keybinding, mode):
    """Remove keybinding from registry.

    See config/configcommands.unbind for the corresponding command.
    """
    if mode in [Modes.IMAGE, Modes.THUMBNAIL, Modes.LIBRARY] \
            and keybinding in _registry[Modes.GLOBAL]:
        del _registry[Modes.GLOBAL][keybinding]
    elif keybinding in _registry[mode]:
        del _registry[mode][keybinding]
    else:
        raise cmdexc.CommandError("No binding found for '%s'" % (keybinding))


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


_registry = {mode: Bindings() for mode in Modes}


def get(mode):
    """Return the keybindings of one specific mode."""
    if mode in [Modes.IMAGE, Modes.THUMBNAIL, Modes.LIBRARY]:
        return _registry[mode] + _registry[Modes.GLOBAL]
    return _registry[mode]


def items():
    return _registry.items()


def clear():
    """Clear all keybindings."""
    for bindings in _registry.values():
        bindings.clear()
