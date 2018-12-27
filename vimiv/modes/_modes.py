# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Module for basic mode handling."""


class Mode:
    """Skeleton for a mode.

    Class Attributes:
        _ID: Unique identifier used to compare modes.

    Attributes:
        active: True if the mode is currently active.
        last_mode: Mode that was active before entering this one.
        widget: QWidget associated with this mode.

        _name: Name of the mode used for commands which require a string
            representation.
        _id: The unique identifier used to compare modes.
    """

    _ID = 0

    def __init__(self, name):
        self.active = False
        self.last_mode = None
        self.widget = None
        self._name = name

        # Store global ID as ID and increase it by one
        self._id = Mode._ID
        Mode._ID += 1

    def __eq__(self, other):
        return self._id == other._id

    def __neq__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._id

    @property
    def name(self):
        return self._name

    def __repr__(self):
        return "Modes.%s" % (self.name.upper())


class iterable(type):
    """Metaclass to allow iterating over a class."""

    def __iter__(self):
        return self.classiter()


class Modes(metaclass=iterable):
    """Storage class for all modes.

    The class is iterable to allow `for mode in Modes`.
    """
    GLOBAL = Mode("global")
    IMAGE = Mode("image")
    LIBRARY = Mode("library")
    THUMBNAIL = Mode("thumbnail")
    COMMAND = Mode("command")
    MANIPULATE = Mode("manipulate")

    _modes = [GLOBAL, IMAGE, LIBRARY, THUMBNAIL, COMMAND, MANIPULATE]

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


# Initialize default values for modes
for mode in Modes:
    if mode == Modes.IMAGE:
        mode.active = True # Default mode
        mode.last_mode = Modes.LIBRARY
    else:
        mode.last_mode = Modes.IMAGE


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
