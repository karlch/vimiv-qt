# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Functions to read and write command history."""

import os

from vimiv.utils import xdg


def read():
    """Read command history from file."""
    filename = xdg.join_vimiv_data("history")
    # Create empty history file
    if not os.path.isfile(filename):
        with open(filename, "w") as f:
            f.write("")
        return []
    # Read from file
    history = []
    with open(filename) as f:
        for line in f.readlines():
            history.append(line.rstrip("\n"))
    return history


def write(commands):
    """Write command history to file.

    Args:
        commands: List of commands.
    """
    filename = xdg.join_vimiv_data("history")
    with open(filename, "w") as f:
        for command in commands:
            f.write(command + "\n")
