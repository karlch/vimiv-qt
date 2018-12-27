# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Classes and functions to store, enter and leave modes.

Module Attributes:
    _modes: Modes dictionary storing all possible modes.
    signals: Signals class to store the signals relevant for entering and
        leaving modes.
"""

import logging

from PyQt5.QtCore import pyqtSignal, QObject

from ._modes import Mode, Modes
from vimiv.commands import commands
from vimiv.config import keybindings
from vimiv.gui import statusbar


class Signals(QObject):
    """Qt signals to emit when entering and leaving modes.

    Signals:
        entered: Emitted when a mode is entered.
            arg1: Name of the mode entered.
        left: Emitted when a mode is left.
            arg1: Name of the mode left.
    """

    entered = pyqtSignal(Mode)
    left = pyqtSignal(Mode)


signals = Signals()


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
    if isinstance(mode, str):
        mode = Modes.get_by_name(mode)
    # Store last mode
    last_mode = current()
    if mode == last_mode:
        logging.debug("Staying in mode %s", mode.name)
        return
    if last_mode:
        logging.debug("Leaving mode %s", last_mode.name)
        last_mode.active = False
        if last_mode not in [Modes.COMMAND, Modes.MANIPULATE]:
            mode.last_mode = last_mode
    # Enter new mode
    mode.active = True
    mode.widget.show()
    mode.widget.setFocus()
    if mode.widget.hasFocus():
        logging.debug("%s widget focused", mode)
    else:
        logging.debug("Could not focus %s widget", mode)
    signals.entered.emit(mode)
    logging.debug("Entered mode %s", mode)


def leave(mode):
    """Leave the mode 'mode'."""
    if isinstance(mode, str):
        mode = Modes.get_by_name(mode)
    enter(mode.last_mode)
    signals.left.emit(mode)


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
    if isinstance(mode, str):
        mode = Modes.get_by_name(mode)
    if mode.widget.isVisible():
        leave(mode)
    else:
        enter(mode)


def current():
    """Return the currently active mode."""
    for mode in Modes:
        if mode.active:
            return mode
    return Modes.IMAGE


@statusbar.module("{mode}")
def get_active_name():
    """Current mode."""
    return current().name.upper()


def last():
    """Return the mode active before the current one."""
    return current().last_mode
