# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handler to deal with entering and leaving modes."""

import logging

from PyQt5.QtCore import pyqtSignal, QObject

from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.modes.modereg import modes
from vimiv.utils import objreg


class Signals(QObject):
    """Signals for modehandler.

    Signals:
        toggled: Emitted with the widget name when a widget was toggled.
    """

    enter = pyqtSignal(str)
    leave = pyqtSignal(str)


signals = Signals()


@keybindings.add("gt", "enter thumbnail")
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
    signals.enter.emit(mode)
    logging.debug("Entered mode %s", mode)


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
    signals.leave.emit(mode)


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
