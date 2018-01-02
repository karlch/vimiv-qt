# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Custom exceptions raised by modules in vimiv.commands."""


class ArgumentError(Exception):
    """Raised if a command was called with wrong arguments."""


class CommandError(Exception):
    """Raised if a command failed to run correctly."""


class CommandWarning(Exception):
    """Raised if a command wants to show the user a warning."""


class CommandNotFound(Exception):
    """Raised if a command does not exist for a specific mode."""
