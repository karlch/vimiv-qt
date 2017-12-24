# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Handler to deal with entering and leaving modes."""

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.modes.modereg import modes
from vimiv.utils import objreg


@keybindings.add("gl", "enter library")
@keybindings.add("gi", "enter image")
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
    return active_mode.name.upper()


def last():
    """Return the name of the mode active before the current one."""
    active_mode = get_active_mode()
    return active_mode.last_mode
