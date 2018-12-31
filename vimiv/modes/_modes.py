# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Module for basic mode handling."""


import abc


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
        return "Modes.%s" % (self.name.upper())


class MainMode(Mode):
    """Main mode class used for everything but command mode."""

    def _set_last(self, mode):
        """Store any mode except for command and manipulate."""
        if mode not in [Modes.COMMAND, Modes.MANIPULATE]:
            self._last = mode


class CommandMode(Mode):
    """Command mode class."""

    def _set_last(self, mode):
        """Store any mode except for command."""
        if mode != self:
            self._last = mode


class Iterable(type):
    """Metaclass to allow iterating over a class."""

    def __iter__(cls):
        return cls.classiter()  # Defer acual iteration to the class


class Modes(metaclass=Iterable):
    """Storage class for all modes.

    The class is iterable to allow `for mode in Modes`.
    """

    GLOBAL = MainMode("global")
    IMAGE = MainMode("image")
    LIBRARY = MainMode("library")
    THUMBNAIL = MainMode("thumbnail")
    COMMAND = CommandMode("command")
    MANIPULATE = MainMode("manipulate")

    _modes = [GLOBAL, IMAGE, LIBRARY, THUMBNAIL, COMMAND, MANIPULATE]

    @classmethod
    def init(cls):
        """Initialize default values for mode."""
        for mode in cls._modes:
            if mode == Modes.IMAGE:
                mode.active = True  # Default mode
                mode.last = mode.last_fallback = Modes.LIBRARY
            else:
                mode.last = mode.last_fallback = Modes.IMAGE

    @staticmethod
    def get_by_name(name):
        """Retrieve Mode class by name."""
        for mode in Modes:
            if mode.name == name:
                return mode
        raise KeyError("'%s' is not a valid mode" % (name.upper()))

    @classmethod
    def classiter(cls):
        return iter(cls._modes)


Modes.init()  # Set default values


def modewidget(mode):
    """Decorator to assign a widget to a mode.

    The decorator decorates the __init__ function of a QWidget class storing
    the created component as the widget associated to the mode.

    Args:
        mode: The mode to associate the decorated widget with.
    """
    def decorator(component_init):
        def inner(component, *args, **kwargs):
            mode.widget = component
            component_init(component, *args, **kwargs)
        return inner
    return decorator
