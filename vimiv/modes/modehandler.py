# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""ModeHandler singleton to deal with entering and leaving modes."""

import logging

from PyQt5.QtCore import pyqtSignal, QObject

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.modes.modereg import modes
from vimiv.utils import objreg


def init():
    """Initialize the ModeHandler object."""
    ModeHandler()


def instance():
    """Get the ModeHandler object. """
    return objreg.get("mode-handler")


@keybindings.add("gt", "enter thumbnail")
@keybindings.add("gl", "enter library")
@keybindings.add("gi", "enter image")
@commands.argument("mode")
@commands.register()
def enter(mode):
    """Enter the mode 'mode'."""
    instance().enter(mode)


@commands.argument("mode")
@commands.register()
def leave(mode):
    """Leave the mode 'mode.'"""
    instance().leave(mode)


@keybindings.add("tt", "toggle thumbnail")
@keybindings.add("tl", "toggle library")
@commands.argument("mode")
@commands.register()
def toggle(mode):
    """Toggle one mode.

    If mode is currently visible, leave. Else enter.

    Args:
        widget: Name of the mode to toggle.
    """
    qwidget = objreg.get(mode)
    if qwidget.isVisible():
        leave(mode)
    else:
        enter(mode)


def get_active_mode():
    """Return the currently active mode as Mode class."""
    for mode in modes.values():
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
    """

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
            if last_mode.name not in ["command"]:
                modes[mode].last_mode = last_mode.name
        # Enter new mode
        modes[mode].active = True
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
        last_mode = modes[mode].last_mode
        enter(last_mode)
        self.left.emit(mode)
