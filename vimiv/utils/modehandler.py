# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Handler to deal with entering and leaving modes.

Module Attributes:
    modes: Dictionary to store all modes.
"""

import collections

from vimiv.commands import commands
from vimiv.gui import statusbar
from vimiv.utils import objreg


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
        self["global"] = Mode("global")  # For keybindings
        self["image"] = Mode("image")
        self["image"].active = True  # Default mode
        self["library"] = Mode("library")
        self["command"] = Mode("command")


modes = Modes()


@commands.argument("mode")
@commands.register()
def enter(mode):
    """Enter a mode.

    Saves the last mode, sets the new mode as active and focuses the widget
    corresponding to the new mode.

    Args:
        mode: The mode to enter.
    """
    # Store last mode
    last_mode = get_active_mode()
    if last_mode:
        last_mode.active = False
        if last_mode not in ["command"]:
            modes[mode].last_mode = last_mode.name
    # Enter new mode
    modes[mode].active = True
    widget = objreg.get(mode)
    widget.show()
    widget.setFocus()


@commands.argument("mode")
@commands.register()
def leave(mode):
    """Leave a mode.

    Enters the mode that was active before the mode to leave.

    Args:
        mode: The mode to leave.
    """
    last_mode = modes[mode].last_mode
    enter(last_mode)


def get_active_mode():
    """Return the currently active mode as Mode class."""
    for mode in modes.values():
        if mode.active:
            return mode


@statusbar.module("{mode}")
def current():
    """Return the name of the currently active mode."""
    active_mode = get_active_mode()
    if active_mode:
        return active_mode.name.upper()
    return ""
