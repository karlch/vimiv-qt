# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""TODO"""


import abc
import logging

from PyQt5.QtCore import pyqtSignal, QObject


class NoModeError(Exception):
    """Raised when there is no mode to operate on."""


class Mode(abc.ABC):
    """Skeleton for a mode as abstract base class.

    The child must implement the _set_last method which defines which
    modes are saved as last mode. This is required as in command mode, any mode
    can be the last mode which is supposed to be focused when leaving the
    command line, but e.g. in library mode when toggling the library we should
    never enter manipulate.

    Class Attributes:
        _ID: Unique identifier used to compare modes.

    Attributes:
        active: True if the mode is currently active.
        last_fallback: Mode to use as _last in case _last was closed.
        widget: QWidget associated with this mode.

        _last: Mode that was active before entering this one.
        _name: Name of the mode used for commands which require a string
            representation.
        _id: The unique identifier used to compare modes.
    """

    _ID = 0

    def __init__(self, name):
        self.active = False
        self.last_fallback = None
        self.widget = None

        self._last = None
        self._name = name

        # Store global ID as ID and increase it by one
        self._id = Mode._ID
        Mode._ID += 1

    @property
    def identifier(self):
        """Value of _id to compare to other modes as property."""
        return self._id

    @property
    def last(self):
        """Value of last mode as property."""
        return self._last

    @last.setter
    def last(self, mode):
        self._set_last(mode)  # To be implemented by the child class

    def reset_last(self):
        """Reset last mode to the fallback value.

        This can be used when the last mode was closed.
        """
        self._last = self.last_fallback

    @abc.abstractmethod
    def _set_last(self, mode):
        pass

    def __eq__(self, other):
        if isinstance(other, Mode):
            return self.identifier == other.identifier
        return False

    def __hash__(self):
        return self._id

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return "Mode.%s" % (self.name.upper())


def get_by_name(name: str) -> Mode:
    """Retrieve Mode class by name.

    Args:
        name: Name of the mode to retrieve.
    Return:
        The corresponding :class:`vimiv.api.modes.Mode` class.
    """
    for mode in ALL:
        if mode.name.lower() == name.lower():
            return mode
    raise KeyError("'%s' is not a valid mode" % (name.upper()))


def widget(mode):
    """Decorator to assign a widget to a mode.

    The decorator decorates the __init__ function of a QWidget class storing
    the created component as the widget associated to the mode. This is used
    when entering a mode to focus the widget which is assigned to this mode.

    Args:
        mode: The mode to associate the decorated widget with.
    """
    def decorator(component_init):
        def inner(component, *args, **kwargs):
            mode.widget = component
            component_init(component, *args, **kwargs)
        return inner
    return decorator


class _MainMode(Mode):
    """Main mode class used for everything but command mode."""

    def _set_last(self, mode):
        """Store any mode except for command and manipulate."""
        if mode not in [COMMAND, MANIPULATE]:
            self._last = mode


class _CommandMode(Mode):
    """Command mode class."""

    def _set_last(self, mode):
        """Store any mode except for command."""
        if mode != self:
            self._last = mode


# Create all modes
GLOBAL = _MainMode("global")
IMAGE = _MainMode("image")
LIBRARY = _MainMode("library")
THUMBNAIL = _MainMode("thumbnail")
COMMAND = _CommandMode("command")
MANIPULATE = _MainMode("manipulate")


# Utility lists to allow iterating
ALL = [IMAGE, LIBRARY, THUMBNAIL, COMMAND, MANIPULATE, GLOBAL]
GLOBALS = [IMAGE, LIBRARY, THUMBNAIL]


class _Signals(QObject):
    """Simple QObject containing mode related signals.

    Signals:
        entered: Emitted when a mode is entered.
            arg1: Name of the mode entered.
            arg2: Name of the mode left.
        left: Emitted when a mode is left.
            arg1: Name of the mode left.
    """

    entered = pyqtSignal(Mode, Mode)
    left = pyqtSignal(Mode)


signals = _Signals()


def enter(mode: Mode):
    """Enter another mode.

    Set the current mode to `mode` and focus the widget which is asigned to
    `mode`.

    Args:
        mode: The mode to enter.
    """
    # Store last mode
    last_mode = current()
    if mode == last_mode:
        logging.debug("Staying in mode %s", mode.name)
        return
    if last_mode:
        logging.debug("Leaving mode %s", last_mode.name)
        last_mode.active = False
        mode.last = last_mode
    # Enter new mode
    mode.active = True
    mode.widget.show()
    mode.widget.setFocus()
    if mode.widget.hasFocus():
        logging.debug("%s widget focused", mode)
    else:
        logging.debug("Could not focus %s widget", mode)
    signals.entered.emit(mode, last_mode)
    logging.debug("Entered mode %s", mode)


def leave(mode: Mode) -> None:
    """Leave the mode `mode`.

    Enter the mode which was focused before `mode` and close the widget
    assigned to `mode`.

    Args:
        mode: The mode to leave.
    """
    enter(mode.last)
    signals.left.emit(mode)
    # Reset the last mode when leaving a specific mode as leaving means closing
    # the widget and we do not want to re-open a closed widget implicitly
    mode.last.reset_last()


def toggle(mode: Mode) -> None:
    """Toggle the mode `mode`.

    If the mode is currently visible, leave it. Otherwise enter it.

    Args:
        mode: The mode to leave.
    """
    if mode.widget.isVisible():
        leave(mode)
    else:
        enter(mode)


def current() -> Mode:
    """Return the currently active mode."""
    for mode in ALL:
        if mode.active:
            return mode
    raise NoModeError()


def _init():
    """Initialize default values for each mode."""
    for _mode in ALL:
        if _mode == IMAGE:
            _mode.active = True  # Default mode
            _mode.last = _mode.last_fallback = LIBRARY
        else:
            _mode.last = _mode.last_fallback = IMAGE


_init()
