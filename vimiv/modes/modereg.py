# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Registry to keep track of all modes.

Module Attributes:
    modes: Dictionary to store all modes.
"""

import collections

class Mode():
    """Skeleton of a mode.

    Attributes:
        active: True if the mode is currently active.
        name: Name of the mode as string.
        last_mode: Name of the mode that was focused before entering this mode.
    """

    def __init__(self, name):
        self.active = False
        self.name = name
        self.last_mode = name


class Modes(collections.UserDict):
    """Dictionary to store all modes."""

    def __init__(self):
        """Init dictionary and create modes."""
        super().__init__()
        self["global"] = Mode("global")  # For keybindings and commands
        self["image"] = Mode("image")
        self["image"].active = True  # Default mode
        self["library"] = Mode("library")
        self["command"] = Mode("command")


modes = Modes()
