# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Singleton to run commands."""

import collections
import logging
import re

from vimiv.commands import runners
from vimiv.modes import modehandler
from vimiv.utils import objreg, pathreceiver


def init():
    """Create CommandRunner object."""
    CommandRunner()


def instance():
    """Get the CommandRunner object."""
    return objreg.get("cmd-runner")


def run(command, mode=None):
    """Run 'command' using the CommandRunner."""
    if mode is None:
        mode = modehandler.current()
    instance()(":", command, mode)


class CommandRunner(collections.UserDict):
    """Singleton to run commands."""

    @objreg.register("cmd-runner")
    def __init__(self):
        super().__init__()
        self["command"] = runners.CommandRunner()
        self["external"] = runners.ExternalRunner()
        self["alias"] = runners.AliasRunner()

    def __call__(self, prefix, command, mode):
        """Run a command using the appropriate runner.

        Args:
            prefix: One of ":", "/" for command and search.
            command: Command text to parse.
            mode: Mode in which the command should be run.
        """
        # Dereference aliases first
        command = self["alias"](command, mode)
        # Expand wildcards
        command = self._expand_wildcards(command, mode)
        if prefix == ":" and command.startswith("!"):
            self["external"](command.lstrip(":!"))
        elif prefix == ":":
            self["command"](command, mode)
        elif prefix == "/":
            raise NotImplementedError("Search not implemented yet")
        else:
            logging.error("Unknown prefix '%s'", prefix)

    def _expand_wildcards(self, command, mode):
        current = pathreceiver.current(mode)
        command = re.sub(r'(?<!\\)%', current, command)
        return command
