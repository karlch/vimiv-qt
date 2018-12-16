# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Store and change settings.

Module attributes:
    signals: Signals for the settings module.

    _storage: Initialized Storage object to store settings globally.
"""

import collections
import logging
from abc import ABC, abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.utils import strconvert, misc


class Signals(QObject):
    """Signals for the settings module.

    Signals:
        changed: Emitted when a setting has changed.
            arg1: Name of the setting changed.
            arg2: New value of the changed setting
    """

    changed = pyqtSignal(str, object)


signals = Signals()


class Storage(collections.UserDict):
    """Stores all settings.

    Currently a plain dictionary but may become fancier in the future.
    """


_storage = Storage()


def get(name):
    """Get a Setting object from the storage.

    Args:
        name: Name of the setting as stored in the storage.
    Return:
        The actual python Setting object associated with the name.
    """
    return _storage[name]


def get_value(name):
    """Get the current value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
    Return:
        The value of the setting in its python data type.
    """
    return _storage[name].get_value()


def override(name, new_value):
    """Override the value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
        new_value: Value to override the setting with as string.
    """
    setting = _storage[name]
    setting.override(new_value)


def toggle(name):
    """Toggle the value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
    """
    setting = _storage[name]
    if not isinstance(setting, BoolSetting):
        raise TypeError("Setting %s does not store a bool." % (name))
    setting.toggle()


def add_to(name, value):
    """Add a value to a setting.

    Args:
        name: Name of the setting as stored in the storage.
        new_value: Value to add to the setting with as string.
    """
    setting = _storage[name]
    if not isinstance(setting, NumberSetting):
        raise TypeError("Setting %s does not store a number." % (name))
    setting.add(value)


def multiply_with(name, value):
    """Multiply a setting with a value.

    Args:
        name: Name of the setting as stored in the storage.
        new_value: Value to multiply the setting with with as string.
    """
    setting = _storage[name]
    if not isinstance(setting, NumberSetting):
        raise TypeError("Setting %s does not store a number." % (name))
    setting.multiply(value)


def reset():
    """Reset all settings to their default value."""
    for setting in _storage.values():
        setting.set_to_default()


def set_to_default(name):
    """Set one setting back to default.

    Args:
        name: Name of the setting as stored in the storage.
    """
    _storage[name].set_to_default()


def store(init):
    """Decorator to store a setting as soon as it is initialized."""
    def setting_init(setting, name, default_value, desc="", suggestions=None):
        """Initialize the setting and store it."""
        init(setting, name, default_value, desc, suggestions)
        _storage[name] = setting
    return setting_init


def items():
    return _storage.items()


def names():
    return _storage.keys()


class Setting(ABC):
    """Stores a setting and its attributes.

    This class can not be used directly. Instead it is used as BaseClass for
    different types of settings.

    Attributes:
        name: Name of the setting as string.

        _default_value: Default value of the setting stored in its python type.
        _value: Value of the setting stored in its python type.
    """

    @store
    def __init__(self, name, default_value, desc="", suggestions=None):
        """Initialize attributes with default values.

        Args:
            name: Name of the setting to initialize.
            default_value: Default value of the setting to start with.
            desc: Description of the setting.
            suggestions: List of useful values to show in completion widget.
        """
        super(Setting, self).__init__()
        self.name = name
        self._default_value = default_value
        self._value = default_value
        self.desc = desc
        self._suggestions = suggestions

    def get_default(self):
        return self._default_value

    def get_value(self):
        return self._value

    def is_default(self):
        return self._value == self._default_value

    def set_to_default(self):
        self._value = self._default_value

    @abstractmethod
    def override(self, new_value):
        """Override the stored value with a new value.

        Must be implemented by the child class as this fails or succeeds
        depending on the type of value.
        """

    def suggestions(self):
        """Return a list of valid or useful suggestions for the setting.

        Used by the completion widget.
        """
        return self._suggestions if self._suggestions else []


class BoolSetting(Setting):
    """Stores a boolean setting."""

    def override(self, new_value):
        self._value = strconvert.to_bool(new_value)

    def toggle(self):
        self._value = not self._value

    def suggestions(self):
        return ["True", "False"]

    def __str__(self):
        return "Bool"


class NumberSetting(Setting, ABC):
    """Used as ABC for Int and Float settings.

    This allows using isinstance(setting, NumberSetting) for add_to and
    multiply functions.

    Attributes:
        min_value: Minimum value allowed for this setting.
        max_value: Maximum value allowed for this setting.
    """

    def __init__(self, name, default_value, desc="", suggestions=None,
                 min_value=None, max_value=None):
        """Additionally allow setting minimum and maximum value."""
        super().__init__(name, default_value, desc, suggestions)
        self.min_value = min_value
        self.max_value = max_value

    @abstractmethod
    def override(self, new_value):
        """Must still be overridden."""


class IntSetting(NumberSetting):
    """Stores an integer setting."""

    def override(self, new_value):
        value = strconvert.to_int(new_value, allow_sign=True)
        self._value = misc.clamp(value, self.min_value, self.max_value)

    def add(self, value):
        """Add a value to the currently stored integer.

        Args:
            value: The integer value to add as string.
        """
        value = strconvert.to_int(value, allow_sign=True)
        self._value = misc.clamp(self._value + value, self.min_value,
                                 self.max_value)

    def multiply(self, value):
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        value = strconvert.to_int(value, allow_sign=True)
        self._value = misc.clamp(self._value * value, self.min_value,
                                 self.max_value)

    def __str__(self):
        return "Integer"


class FloatSetting(NumberSetting):
    """Stores a float setting."""

    def override(self, new_value):
        value = strconvert.to_float(new_value, allow_sign=True)
        self._value = misc.clamp(value, self.min_value, self.max_value)

    def add(self, value):
        """Add a value to the currently stored float.

        Args:
            value: The float value to add as string.
        """
        value = strconvert.to_float(value, allow_sign=True)
        self._value = misc.clamp(self._value + value, self.min_value,
                                 self.max_value)

    def multiply(self, value):
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        value = strconvert.to_float(value, allow_sign=True)
        self._value = misc.clamp(self._value * value, self.min_value,
                                 self.max_value)

    def __str__(self):
        return "Float"


class ThumbnailSizeSetting(Setting):
    """Stores a thumbnail size setting.

    This setting is stored as integer value which must be one of 64, 128, 256,
    512.
    """

    ALLOWED_VALUES = [64, 128, 256, 512]

    def override(self, new_value):
        """Override the setting with a new thumbnail size.

        Args:
            new_value: String containing.
        """
        new_value = strconvert.to_int(new_value)
        if new_value not in self.ALLOWED_VALUES:
            raise ValueError("Thumnbail size must be one of 64, 128, 256, 512")
        self._value = new_value

    def increase(self):
        """Increase thumbnail size."""
        index = self.ALLOWED_VALUES.index(self._value)
        index += 1
        index = min(index, len(self.ALLOWED_VALUES) - 1)
        self._value = self.ALLOWED_VALUES[index]

    def decrease(self):
        """Decrease thumbnail size."""
        index = self.ALLOWED_VALUES.index(self._value)
        index -= 1
        index = max(index, 0)
        self._value = self.ALLOWED_VALUES[index]

    def suggestions(self):
        return self.ALLOWED_VALUES

    def __str__(self):
        return "ThumbSize"


class StrSetting(Setting):
    """Stores a string setting."""

    def override(self, new_value):
        assert isinstance(new_value, str), "Type of StrSetting must be str"
        self._value = new_value

    def __str__(self):
        return "String"


class Names:
    """Simple class which stores the string names of all settings."""

    SHUFFLE = "shuffle"
    STYLE = "style"

    SEARCH_IGNORE_CASE = "search.ignore_case"
    # SEARCH_INCREMENTAL = "search.incremental"

    IMAGE_AUTOPLAY = "image.autoplay"
    IMAGE_AUTOWRITE = "image.autowrite"
    IMAGE_OVERZOOM = "image.overzoom"

    LIBRARY_WIDTH = "library.width"
    LIBRARY_SHOW_HIDDEN = "library.show_hidden"
    LIBRARY_FILE_CHECK_AMOUNT = "library.file_check_amount"

    THUMBNAIL_SIZE = "thumbnail.size"

    SLIDESHOW_DELAY = "slideshow.delay"
    SLIDESHOW_INDICATOR = "slideshow.indicator"

    STATUSBAR_COLLAPSE_HOME = "statusbar.collapse_home"
    STATUSBAR_SHOW = "statusbar.show"
    STATUSBAR_MESSAGE_TIMEOUT = "statusbar.message_timeout"


def init_defaults():
    """Store default values of all settings."""
    # General
    BoolSetting(Names.SHUFFLE, False, desc="Randomly shuffle images")
    StrSetting(Names.STYLE, "default")

    # Search
    BoolSetting(Names.SEARCH_IGNORE_CASE, True,
                desc="Ignore case when searching, i.e. 'A' and 'a' are equal")

    # Image
    BoolSetting(Names.IMAGE_AUTOPLAY, True,
                desc="Start playing animations on open")
    BoolSetting(Names.IMAGE_AUTOWRITE, True, desc="Save images on changes")
    FloatSetting(Names.IMAGE_OVERZOOM, 1.0,
                 desc="Maximum scale to apply trying to fit image to window",
                 suggestions=["1.0", "1.5", "2.0", "5.0"],
                 min_value=1.0)

    # Library
    FloatSetting("library.width", 0.3,
                 desc="Width of the library as fraction of main window size",
                 suggestions=["0.2", "0.3", "0.4", "0.5"], min_value=0.05,
                 max_value=0.95)
    BoolSetting("library.show_hidden", False,
                desc="Show hidden files in the library")
    IntSetting("library.file_check_amount", 30,
               desc="Number of files to check when calculating directory size",
               suggestions=["10", "30", "100", "0"])

    # Thumbnail
    ThumbnailSizeSetting("thumbnail.size", 128, desc="Size of thumbnails")

    # Slideshow
    FloatSetting("slideshow.delay", 2.0,
                 desc="Delay to next image in slideshow", min_value=0.5)
    StrSetting("slideshow.indicator", "slideshow:",
               desc="Text to display in statusbar when slideshow is running")

    # Statusbar
    BoolSetting("statusbar.collapse_home", True,
                desc="Collapse /home/user to ~ in statusbar")
    BoolSetting("statusbar.show", True, desc="Always display the statusbar")
    IntSetting("statusbar.message_timeout", 5000,
               desc="Time in ms until statusbar messages are removed",
               min_value=500)
    StrSetting("statusbar.left", "{pwd}")
    StrSetting("statusbar.left_image",
               "{index}/{total} {basename} [{zoomlevel}]")
    StrSetting("statusbar.left_thumbnail",
               "{thumbnail-index}/{thumbnail-total} {thumbnail-name}")
    StrSetting("statusbar.center_thumbnail",
               "{thumbnail-size}")
    StrSetting("statusbar.center", "{slideshow-indicator} {slideshow-delay}")
    StrSetting("statusbar.right", "{keys}  {mode}")

    # Log message
    logging.info("Initialized default settings")
