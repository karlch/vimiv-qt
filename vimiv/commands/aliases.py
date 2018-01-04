# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Aliases singleton to store and receive aliases."""

import collections

from vimiv import modes
from vimiv.commands import commands, cmdexc
from vimiv.utils import objreg


def instance():
    """Get the Aliases object."""
    return objreg.get("aliases")


def init():
    """Initialize the Aliases object."""
    Aliases()


def get(mode):
    """Return all aliases for the mode 'mode'."""
    return instance().get(mode)


@commands.argument("mode", optional=True, default="global")
@commands.argument("command", nargs="*")
@commands.argument("name")
@commands.register()
def alias(name, command, mode="global"):
    """Add an alias for a command."""
    assert isinstance(command, list), "Aliases defined as list via nargs='*'"
    instance().alias(name, command, mode)


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

    def alias(self, name, command, mode):
        """Add an alias for a command.

        Args:
            name: Name of the alias to create.
            command: Name of the command to alias.
            mode: Mode in which the command is valid.
        """
        command = " ".join(command)
        if name in commands.registry[mode]:
            raise cmdexc.CommandError(
                "Not overriding default command %s" % (name))
        self[mode][name] = command
