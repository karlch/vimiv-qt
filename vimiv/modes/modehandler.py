# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""ModeHandler singleton to deal with entering and leaving modes."""

import collections
import logging

from PyQt5.QtCore import pyqtSignal, QObject

from vimiv import modes
from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.utils import objreg


def init():
    """Initialize the Modes and ModeHandler objects."""
    ModeHandler()


def instance():
    """Get the ModeHandler object."""
    return objreg.get("mode-handler")


@keybindings.add("gm", "enter manipulate")
@keybindings.add("gt", "enter thumbnail")
@keybindings.add("gl", "enter library")
@keybindings.add("gi", "enter image")
@commands.argument("mode")
@commands.register()
def enter(mode):
    """Enter another mode.

    **syntax:** ``:enter mode``

    positional arguments:
        * ``mode``: The mode to enter (image/library/thumbnail/manipulate).
    """
    instance().enter(mode)


def leave(mode):
    """Leave the mode 'mode'."""
    instance().leave(mode)


@keybindings.add("tm", "toggle manipulate")
@keybindings.add("tt", "toggle thumbnail")
@keybindings.add("tl", "toggle library")
@commands.argument("mode")
@commands.register()
def toggle(mode):
    """Toggle one mode.

    **syntax:** ``:toggle mode``.

    If the mode is currently visible, leave it. Otherwise enter it.

    positional arguments:
        * ``mode``: The mode to toggle (image/library/thumbnail/manipulate).
    """
    qwidget = objreg.get(mode)
    if qwidget.isVisible():
        leave(mode)
    else:
        enter(mode)


def get_active_mode():
    """Return the currently active mode as Mode class."""
    for mode in instance().modes.values():
        if mode.active:
            return mode
    return None


def current():
    """Return the name of the currently active mode."""
    return get_active_mode().name


@statusbar.module("{mode}")
def current_formatted():
    return current().upper()


def last():
    """Return the name of the mode active before the current one."""
    active_mode = get_active_mode()
    return active_mode.last_mode


class ModeHandler(QObject):
    """Singleton to enter and leave modes.

    Attributes:
        modes: Dictionary storing all modes.

    Signals:
        entered: Emitted when a mode is entered.
            arg1: Name of the mode entered.
        left: Emitted when a mode is left.
            arg1: Name of the mode left.
    """

    entered = pyqtSignal(str)
    left = pyqtSignal(str)

    @objreg.register("mode-handler")
    def __init__(self):
        super().__init__()
        self.modes = Modes()

    def enter(self, mode):
        """Enter a mode.

        Saves the last mode, sets the new mode as active and focuses the widget
        corresponding to the new mode.

        Args:
            mode: The mode to enter.
        """
        # Store last mode
        last_mode = get_active_mode()
        if mode == last_mode.name:
            logging.debug("Staying in mode %s", mode)
            return
        if last_mode:
            logging.debug("Leaving mode %s", last_mode.name)
            last_mode.active = False
            if last_mode.name not in ["command", "manipulate"]:
                self.modes[mode].last_mode = last_mode.name
        # Enter new mode
        self.modes[mode].active = True
        widget = objreg.get(mode)
        widget.show()
        widget.setFocus()
        if widget.hasFocus():
            logging.debug("%s widget focused", mode)
        else:
            logging.debug("Could not focus %s widget", mode)
        self.entered.emit(mode)
        logging.debug("Entered mode %s", mode)

    def leave(self, mode):
        """Leave a mode.

        Enters the mode that was active before the mode to leave.

        Args:
            mode: The mode to leave.
        """
        last_mode = self.modes[mode].last_mode
        enter(last_mode)
        self.left.emit(mode)


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
        self.last_mode = "image" if name != "image" else "library"


class Modes(collections.UserDict):
    """Dictionary to store all modes."""

    def __init__(self):
        """Init dictionary and create modes."""
        super().__init__()
        for name in modes.__names__:
            self[name] = Mode(name)
        self["image"].active = True  # Default mode
