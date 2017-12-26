# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Store and change settings.

Module attributes:
    signals: Signals for the settings module.

    _storage: Initialized Storage object to store settings globally.
"""

import collections
import logging
from abc import ABC, abstractmethod

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.utils import strconvert


class Signals(QObject):
    """Signals for the settings module.

    Signals:
        changed: Emitted with name and new value when a setting was changed via
            the :set command.
    """

    changed = pyqtSignal(str, object)


signals = Signals()


class Storage(collections.UserDict):
    """Stores all settings."""


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


def store(init):
    """Decorator to store a setting as soon as it is initialized."""
    def setting_init(setting, name, default_value):
        """Initialize the setting and store it."""
        init(setting, name, default_value)
        _storage[name] = setting
    return setting_init


def items():
    return _storage.items()


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
    def __init__(self, name, default_value):
        """Initialize attributes with default values.

        Args:
            name: Name of the setting to initialize.
            default_value: Default value of the setting to start with.
        """
        super(Setting, self).__init__()
        self.name = name
        self._default_value = default_value
        self._value = default_value

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


class BoolSetting(Setting):
    """Stores a boolean setting."""

    def override(self, new_value):
        self._value = strconvert.to_bool(new_value)

    def toggle(self):
        self._value = not self._value


class NumberSetting(Setting, ABC):
    """Used as ABC for Int and Float settings.

    This allows using isinstance(setting, NumberSetting) for add_to and
    multiply functions.
    """

    @abstractmethod
    def override(self, new_value):
        """Must still be overridden."""


class IntSetting(NumberSetting):
    """Stores an integer setting."""

    def override(self, new_value):
        self._value = strconvert.to_int(new_value)

    def add(self, value):
        """Add a value to the currently stored integer.

        Args:
            value: The integer value to add as string.
        """
        value = strconvert.to_int(value, allow_sign=True)
        self._value += value

    def multiply(self, value):
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        value = strconvert.to_int(value, allow_sign=True)
        self._value *= value


class FloatSetting(NumberSetting):
    """Stores a float setting."""

    def override(self, new_value):
        self._value = strconvert.to_float(new_value)

    def add(self, value):
        """Add a value to the currently stored float.

        Args:
            value: The float value to add as string.
        """
        value = strconvert.to_float(value, allow_sign=True)
        self._value += value

    def multiply(self, value):
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        value = strconvert.to_float(value, allow_sign=True)
        self._value *= value


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


class StrSetting(Setting):
    """Stores a string setting."""

    def override(self, new_value):
        assert isinstance(new_value, str), "Type of StrSetting must be str"
        self._value = new_value


def init_defaults():
    """Store default values of all settings."""
    # General
    BoolSetting("shuffle", False)
    BoolSetting("search_case_sensitive", False)
    BoolSetting("incsearch", True)
    StrSetting("style", "default")

    # Image
    BoolSetting("image.autoplay_animations", True)
    # BoolSetting("image.rescale_svg", True)
    FloatSetting("image.overzoom", 1.0)

    # Library
    IntSetting("library.width", 300)
    BoolSetting("library.expand", True)
    BoolSetting("library.show_hidden", False)
    IntSetting("library.file_check_amount", 30)

    # Thumbnail
    ThumbnailSizeSetting("thumbnail.size", 128)

    # Slideshow
    FloatSetting("slideshow.delay", 2.0)
    StrSetting("slideshow.indicator", "slideshow:")

    # Statusbar
    BoolSetting("statusbar.collapse_home", True)
    StrSetting("statusbar.mark_indicator", "[*]")
    BoolSetting("statusbar.show", True)
    IntSetting("statusbar.message_timeout", 5000)
    StrSetting("statusbar.left", "{pwd}")
    StrSetting("statusbar.left_image",
               "{index}/{total} {basename} [{zoomlevel}]")
    StrSetting("statusbar.left_thumbnail",
               "{thumbnail_index}/{thumbnail_total} {thumbnail_name}")
    StrSetting("statusbar.center_thumbnail",
               "{thumbnail_size}")
    StrSetting("statusbar.center", "{slideshow_indicator} {slideshow_delay}")
    StrSetting("statusbar.right", "{keys}  {mode}")

    # Log message
    logging.info("Initialized default settings")
