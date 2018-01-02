# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Store and receive aliases."""

import collections

from vimiv.modes import modereg


class Aliases(collections.UserDict):
    """Store and receive aliases for every mode."""

    def __init__(self):
        super().__init__()
        for mode in modereg.modes:
            self[mode] = {}
        # Add defaults
        self["global"]["q"] = "quit"
        self["image"]["w"] = "write"

    def get(self, mode):
        """Return all aliases for one mode."""
        if mode in ["image", "library", "thumbnail"]:
            return {**self["global"], **self[mode]}
        return self[mode]
