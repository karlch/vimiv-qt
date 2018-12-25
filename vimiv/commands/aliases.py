# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Class and functions to add and get aliases.

Module Attribute:
    _aliases: Dictionary storing aliases initialized with defaults.
"""

import collections

from vimiv import modes
from vimiv.commands import commands, cmdexc
from vimiv.utils import objreg


class Aliases(collections.UserDict):
    """Store and receive aliases for every mode."""

    @objreg.register("aliases")
    def __init__(self):
        super().__init__()
        for mode in modes.__names__:
            self[mode] = {}
        # Add defaults
        self["global"]["q"] = "quit"
        self["image"]["w"] = "write"

    def get(self, mode):
        """Return all aliases for one mode."""
        if mode in ["image", "library", "thumbnail"]:
            return {**self["global"], **self[mode]}
        return self[mode]


_aliases = Aliases()


def get(mode):
    """Return all aliases for the mode 'mode'."""
    if mode in ["image", "library", "thumbnail"]:
        return {**_aliases["global"], **_aliases[mode]}
    return _aliases[mode]


@commands.argument("mode", optional=True, default="global")
@commands.argument("command", nargs="*")
@commands.argument("name")
@commands.register()
def alias(name, command, mode="global"):
    """Add an alias for a command.

    **syntax:** ``:alias name command [--mode=MODE]``

    The command can be a vimiv command like ``quit`` or an external shell
    command like ``!gimp``.

    positional arguments:
        * ``name``: Name of the newly defined alias.
        * ``command`` Name of the command to alias.

    optional arguments:
        * ``--mode``: Mode in which the alias is valid. Default: ``global``.
    """
    assert isinstance(command, list), "Aliases defined as list via nargs='*'"
    command = " ".join(command)
    if name in commands.registry[mode]:
        raise cmdexc.CommandError(
            "Not overriding default command %s" % (name))
    _aliases[mode][name] = command
