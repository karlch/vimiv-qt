# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Class and functions to add and get aliases.

Module Attribute:
    _aliases: Dictionary storing aliases initialized with defaults.
"""

from typing import List

from vimiv import api


class Aliases(dict):
    """Store and receive aliases for every mode."""

    def __init__(self):
        super().__init__()
        for mode in api.modes.ALL:
            self[mode] = {}
        # Add defaults
        self[api.modes.GLOBAL]["q"] = "quit"
        self[api.modes.IMAGE]["w"] = "write"
        self[api.modes.IMAGE]["wq"] = "write && quit"

    def get(self, mode):
        """Return all aliases for one mode."""
        if mode in api.modes.GLOBALS:
            return {**self[api.modes.GLOBAL], **self[mode]}
        return self[mode]


_aliases = Aliases()


def get(mode):
    """Return all aliases for the mode 'mode'."""
    if mode in api.modes.GLOBALS:
        return {**_aliases[api.modes.GLOBAL], **_aliases[mode]}
    return _aliases[mode]


@api.commands.register()
def alias(name: str, command: List[str], mode: str = "global"):
    """Add an alias for a command.

    **syntax:** ``:alias name command [--mode=MODE]``

    The command can be a vimiv command like ``quit`` or an external shell
    command like ``!gimp``.

    positional arguments:
        * ``name``: Name of the newly defined alias.
        * ``command``: Name of the command to alias.

    optional arguments:
        * ``--mode``: Mode in which the alias is valid. Default: ``global``.
    """
    assert isinstance(command, list), "Aliases defined as list via nargs='*'"
    commandstr = " ".join(command)
    modeobj = api.modes.get_by_name(mode)
    if api.commands.exists(name, modeobj):
        raise api.commands.CommandError(f"Not overriding default command {name}")
    _aliases[modeobj][name] = commandstr
