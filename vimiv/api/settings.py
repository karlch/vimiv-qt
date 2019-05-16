# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Store and change settings.

Module attributes:
    signals: Signals for the settings module.

    _storage: Initialized Storage object to store settings globally.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, ItemsView, List, Union

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.utils import strconvert, clamp


Number = Union[int, float]


_storage: Dict[str, "Setting"] = {}


def get(name: str) -> "Setting":
    """Get a Setting object from the storage.

    Args:
        name: Name of the setting as stored in the storage.
    Return:
        The actual python Setting object associated with the name.
    """
    return _storage[name]


def get_value(name: str) -> Any:
    """Get the current value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
    Return:
        The value of the setting in its python data type.
    """
    return _storage[name].value


def override(name: str, new_value: str) -> None:
    """Override the value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
        new_value: Value to override the setting with as string.
    """
    setting = _storage[name]
    setting.override(new_value)


def toggle(name: str) -> None:
    """Toggle the value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
    """
    setting = _storage[name]
    if not isinstance(setting, BoolSetting):
        raise TypeError("Setting %s does not store a bool." % (name))
    setting.toggle()


def add_to(name: str, value: str) -> None:
    """Add a value to a setting.

    Args:
        name: Name of the setting as stored in the storage.
        new_value: Value to add to the setting with as string.
    """
    setting = _storage[name]
    if not isinstance(setting, NumberSetting):
        raise TypeError("Setting %s does not store a number." % (name))
    setting.add(value)


def multiply_with(name: str, value: str) -> None:
    """Multiply a setting with a value.

    Args:
        name: Name of the setting as stored in the storage.
        new_value: Value to multiply the setting with with as string.
    """
    setting = _storage[name]
    if not isinstance(setting, NumberSetting):
        raise TypeError("Setting %s does not store a number." % (name))
    setting.multiply(value)


def reset() -> None:
    """Reset all settings to their default value."""
    for setting in _storage.values():
        setting.set_to_default()


def set_to_default(name: str) -> None:
    """Set one setting back to default.

    Args:
        name: Name of the setting as stored in the storage.
    """
    _storage[name].set_to_default()


def items() -> ItemsView[str, "Setting"]:
    return _storage.items()


class Setting(ABC):
    """Stores a setting and its attributes.

    This class can not be used directly. Instead it is used as BaseClass for
    different types of settings.

    Attributes:
        name: Name of the setting as string.

        _default: Default value of the setting stored in its python type.
        _value: Value of the setting stored in its python type.
    """

    def __init__(
        self,
        name: str,
        default_value: Any,
        desc: str = "",
        suggestions: List[str] = None,
    ):
        """Initialize attributes with default values.

        Args:
            name: Name of the setting to initialize.
            desc: Description of the setting.
            suggestions: List of useful values to show in completion widget.

            _default: Default value of the setting to start with.
        """
        super(Setting, self).__init__()
        self.name = name
        self._default = default_value
        self._value = default_value
        self.desc = desc
        self._suggestions = suggestions
        _storage[name] = self  # Store setting in storage

    @property
    def default(self) -> Any:
        return self._default

    @property
    def value(self) -> Any:
        return self._value

    def is_default(self) -> bool:
        return self.value == self.default

    def set_to_default(self) -> None:
        self._value = self.default

    @abstractmethod
    def override(self, new_value: str) -> None:
        """Override the stored value with a new value.

        Must be implemented by the child class as this fails or succeeds
        depending on the type of value.
        """

    def suggestions(self) -> List[str]:
        """Return a list of valid or useful suggestions for the setting.

        Used by the completion widget.
        """
        return self._suggestions if self._suggestions else []


class BoolSetting(Setting):
    """Stores a boolean setting."""

    def override(self, new_value: str) -> None:
        self._value = strconvert.to_bool(new_value)

    def toggle(self) -> None:
        self._value = not self._value

    def suggestions(self) -> List[str]:
        return ["True", "False"]

    def __str__(self) -> str:
        return "Bool"


class NumberSetting(Setting, ABC):
    """Used as ABC for Int and Float settings.

    This allows using isinstance(setting, NumberSetting) for add_to and
    multiply functions.

    Attributes:
        min_value: Minimum value allowed for this setting.
        max_value: Maximum value allowed for this setting.
    """

    def __init__(
        self,
        name: str,
        default_value: Number,
        desc: str = "",
        suggestions: List[str] = None,
        min_value: Number = None,
        max_value: Number = None,
    ):
        """Additionally allow setting minimum and maximum value."""
        super().__init__(name, default_value, desc, suggestions)
        self.min_value = min_value
        self.max_value = max_value

    @abstractmethod
    def override(self, new_value: str) -> None:
        """Must still be overridden."""

    @abstractmethod
    def add(self, new_value: str) -> None:
        """Must be implemented by child."""

    @abstractmethod
    def multiply(self, new_value: str) -> None:
        """Must be implemented by child."""


class IntSetting(NumberSetting):
    """Stores an integer setting."""

    def override(self, new_value: str) -> None:
        ivalue = strconvert.to_int(new_value, allow_sign=True)
        self._value = clamp(ivalue, self.min_value, self.max_value)

    def add(self, value: str) -> None:
        """Add a value to the currently stored integer.

        Args:
            value: The integer value to add as string.
        """
        ivalue = strconvert.to_int(value, allow_sign=True)
        self._value = clamp(self._value + ivalue, self.min_value, self.max_value)

    def multiply(self, value: str) -> None:
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        ivalue = strconvert.to_int(value, allow_sign=True)
        self._value = clamp(self._value * ivalue, self.min_value, self.max_value)

    def __str__(self) -> str:
        return "Integer"


class FloatSetting(NumberSetting):
    """Stores a float setting."""

    def override(self, new_value: str) -> None:
        fvalue = strconvert.to_float(new_value, allow_sign=True)
        self._value = clamp(fvalue, self.min_value, self.max_value)

    def add(self, value: str) -> None:
        """Add a value to the currently stored float.

        Args:
            value: The float value to add as string.
        """
        fvalue = strconvert.to_float(value, allow_sign=True)
        self._value = clamp(self._value + fvalue, self.min_value, self.max_value)

    def multiply(self, value: str) -> None:
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        fvalue = strconvert.to_float(value, allow_sign=True)
        self._value = clamp(self._value * fvalue, self.min_value, self.max_value)

    def __str__(self) -> str:
        return "Float"


class ThumbnailSizeSetting(Setting):
    """Stores a thumbnail size setting.

    This setting is stored as integer value which must be one of 64, 128, 256,
    512.
    """

    ALLOWED_VALUES = 64, 128, 256, 512

    def override(self, new_value: str) -> None:
        """Override the setting with a new thumbnail size.

        Args:
            new_value: String containing.
        """
        ivalue = strconvert.to_int(new_value)
        if ivalue not in self.ALLOWED_VALUES:
            raise ValueError("Thumbnail size must be one of 64, 128, 256, 512")
        self._value = ivalue

    def increase(self) -> None:
        """Increase thumbnail size."""
        index = self.ALLOWED_VALUES.index(self._value)
        index += 1
        index = min(index, len(self.ALLOWED_VALUES) - 1)
        self._value = self.ALLOWED_VALUES[index]

    def decrease(self) -> None:
        """Decrease thumbnail size."""
        index = self.ALLOWED_VALUES.index(self._value)
        index -= 1
        index = max(index, 0)
        self._value = self.ALLOWED_VALUES[index]

    def suggestions(self) -> List[str]:
        return [str(value) for value in self.ALLOWED_VALUES]

    def __str__(self) -> str:
        return "ThumbSize"


class StrSetting(Setting):
    """Stores a string setting."""

    def override(self, new_value: str) -> None:
        assert isinstance(new_value, str), "Type of StrSetting must be str"
        self._value = new_value

    def __str__(self) -> str:
        return "String"


class _Signals(QObject):
    """Signals for the settings module.

    Signals:
        changed: Emitted when a setting has changed.
            arg1: The changed setting.
    """

    changed = pyqtSignal(Setting)


signals = _Signals()


# Initialize all settings
MONITOR_FS = BoolSetting(
    "monitor_filesystem",
    True,
    desc="Monitor current directory for changes and reload widgets " "automatically",
)
SHUFFLE = BoolSetting("shuffle", False, desc="Randomly shuffle images")
STARTUP_LIBRARY = BoolSetting(
    "startup_library",
    True,
    desc="Enter library at startup if there are no images to show",
)
STYLE = StrSetting("style", "default")
COMMAND_HISTORY_LIMIT = IntSetting(
    "history_limit", 100, desc="Maximum number of commands to store in history"
)

# Search
SEARCH_IGNORE_CASE = BoolSetting(
    "search.ignore_case",
    True,
    desc="Ignore case when searching, i.e. 'A' and 'a' are equal",
)
SEARCH_INCREMENTAL = BoolSetting(
    "search.incremental", True, desc="Automatically filter search results when typing"
)

# Image
IMAGE_AUTOPLAY = BoolSetting(
    "image.autoplay", True, desc="Start playing animations on open"
)
IMAGE_AUTOWRITE = BoolSetting("image.autowrite", True, desc="Save images on changes")
IMAGE_OVERZOOM = FloatSetting(
    "image.overzoom",
    1.0,
    desc="Maximum scale to apply trying to fit image to window",
    suggestions=["1.0", "1.5", "2.0", "5.0"],
    min_value=1.0,
)

# Library
LIBRARY_WIDTH = FloatSetting(
    "library.width",
    0.3,
    desc="Width of the library as fraction of main window size",
    suggestions=["0.2", "0.3", "0.4", "0.5"],
    min_value=0.05,
    max_value=0.95,
)
LIBRARY_SHOW_HIDDEN = BoolSetting(
    "library.show_hidden", False, desc="Show hidden files in the library"
)

# Thumbnail
THUMBNAIL_SIZE = ThumbnailSizeSetting("thumbnail.size", 128, desc="Size of thumbnails")

# Slideshow
SLIDESHOW_DELAY = FloatSetting(
    "slideshow.delay", 2.0, desc="Delay to next image in slideshow", min_value=0.5
)
SLIDESHOW_INDICATOR = StrSetting(
    "slideshow.indicator",
    "slideshow:",
    desc="Text to display in statusbar when slideshow is running",
)

# Statusbar
STATUSBAR_COLLAPSE_HOME = BoolSetting(
    "statusbar.collapse_home", True, desc="Collapse /home/user to ~ in statusbar"
)
STATUSBAR_SHOW = BoolSetting(
    "statusbar.show", True, desc="Always display the statusbar"
)
STATUSBAR_MESSAGE_TIMEOUT = IntSetting(
    "statusbar.message_timeout",
    5000,
    desc="Time in ms until statusbar messages are removed",
    min_value=500,
)
# Statusbar module strings, these are not retrieved by their type
StrSetting("statusbar.left", "{pwd}")
StrSetting("statusbar.left_image", "{index}/{total} {basename} [{zoomlevel}]")
StrSetting(
    "statusbar.left_thumbnail", "{thumbnail-index}/{thumbnail-total} {thumbnail-name}"
)
StrSetting("statusbar.center_thumbnail", "{thumbnail-size}")
StrSetting("statusbar.center", "{slideshow-indicator} {slideshow-delay}")
StrSetting("statusbar.right", "{keys}  {mode}")

# Keyhint widget and related settings
KEYHINT_DELAY = IntSetting(
    "keyhint.delay",
    500,
    desc="Delay (in ms) until the keyhint widget is displayed",
    min_value=0,
)
KEYHINT_TIMEOUT = IntSetting(
    "keyhint.timeout",
    5000,
    desc="Time (in ms) after which partially typed keybindings are cleared",
    min_value=100,
)

# Title module strings, these are not retrieved by their type
StrSetting(
    "title.fallback",
    "vimiv",
    desc="Default window title if no mode specific options exist",
)
StrSetting("title.image", "vimiv - {basename}", desc="Window title in image mode")
