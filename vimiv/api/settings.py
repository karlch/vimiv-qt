# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Store and change settings.

Module attributes:
    _storage: Initialized Storage object to store settings globally.
"""

from abc import ABCMeta, abstractmethod
from typing import Any, Dict, ItemsView, List, Union, Callable

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.sip import wrappertype

from vimiv.utils import clamp


Number = Union[int, float]
NumberStr = Union[Number, str]
BoolStr = Union[bool, str]
IntStr = Union[int, str]
FloatStr = Union[float, str]
Methodtype = Callable[["Setting", Any], Any]


_storage: Dict[str, "Setting"] = {}


def get(name: str) -> "Setting":
    """Get a Setting object from the storage.

    Args:
        name: Name of the setting as stored in the storage.
    Returns:
        The actual python Setting object associated with the name.
    """
    return _storage[name]


def get_value(name: str) -> Any:
    """Get the current value of a setting.

    Args:
        name: Name of the setting as stored in the storage.
    Returns:
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
        value: Value to add to the setting with as string.
    """
    setting = _storage[name]
    if not isinstance(setting, NumberSetting):
        raise TypeError("Setting %s does not store a number." % (name))
    setting += value


def multiply_with(name: str, value: str) -> None:
    """Multiply a setting with a value.

    Args:
        name: Name of the setting as stored in the storage.
        value: Value to multiply the setting with with as string.
    """
    setting = _storage[name]
    if not isinstance(setting, NumberSetting):
        raise TypeError("Setting %s does not store a number." % (name))
    setting *= value


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


def ensure_type(*types: type) -> Callable[[Methodtype], Methodtype]:
    """Decorator to ensure type of value argument is compatible with setting.

    If the value is one of types, it is returned without conversion as these are the
    types supported by the setting. If it is of type string, the method convert of the
    setting is used to try to convert it.

    Args:
        types: Supported types of the setting.
    Raises:
        ValueError: If the conversion fails.
    """

    def decorator(methodconvert: Methodtype) -> Methodtype:
        def convert(self: "Setting", value: Any) -> Any:
            if isinstance(value, types):
                return value
            if isinstance(value, str):
                try:
                    return methodconvert(self, value)
                except ValueError:
                    raise ValueError(f"Cannot convert '{value}' to {self}")
            raise ValueError(
                f"{self.__class__.__qualname__} can only convert String and {self}"
            )

        return convert

    return decorator


class SettingsMeta(wrappertype, ABCMeta):
    """Metaclass to allow setting to be an ABC as well as a QObject."""


class Setting(QObject, metaclass=SettingsMeta):
    """Stores a setting and its attributes.

    This class can not be used directly. Instead it is used as BaseClass for
    different types of settings.

    Attributes:
        name: Name of the setting as string.
        hidden: True if the setting should not be visible in the :set completion.

        _default: Default value of the setting stored in its python type.
        _value: Value of the setting stored in its python type.

    Signals:
        changed: Emitted with the new value if the setting changed.
    """

    changed = pyqtSignal(object)

    def __init__(
        self,
        name: str,
        default_value: Any,
        desc: str = "",
        suggestions: List[str] = None,
        hidden: bool = False,
    ):
        """Initialize attributes with default values.

        Args:
            name: Name of the setting to initialize.
            default_value: Default value of the setting to start with.
            desc: Description of the setting.
            suggestions: List of useful values to show in completion widget.
            hidden: True if the setting should not be visible in the :set completion.
        """
        super().__init__()
        self.name = name
        self._default = default_value
        self._value = default_value
        self.desc = desc
        self.hidden = hidden
        self._suggestions = suggestions
        _storage[name] = self  # Store setting in storage

    def __setattr__(self, name: str, value: Any) -> None:
        """Override setattr to emit changed if the value changed."""
        if name == "_value":
            super().__setattr__(name, value)
            self.changed.emit(value)
        else:
            super().__setattr__(name, value)

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

    @abstractmethod
    def convert(self, value: Any) -> Any:
        """Convert value to setting type before using it.

        Must be implemented by the child as it knows which type to require.
        """


class BoolSetting(Setting):
    """Stores a boolean setting."""

    def override(self, new_value: BoolStr) -> None:
        self._value = self.convert(new_value)

    def toggle(self) -> None:
        self._value = not self._value

    def suggestions(self) -> List[str]:
        return ["True", "False"]

    @ensure_type(bool)
    def convert(self, text: str) -> bool:
        text = text.lower()
        if text in ["yes", "true", "1"]:
            return True
        if text in ["no", "false", "0"]:
            return False
        raise ValueError

    def __str__(self) -> str:
        return "Bool"


class NumberSetting(Setting):
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
        hidden: bool = False,
        min_value: Number = None,
        max_value: Number = None,
    ):
        """Additionally allow setting minimum and maximum value."""
        super().__init__(name, default_value, desc, suggestions, hidden=hidden)
        self.min_value = min_value
        self.max_value = max_value

    @abstractmethod
    def override(self, new_value: NumberStr) -> None:
        """Must still be overridden."""

    @abstractmethod
    def __iadd__(self, value: NumberStr) -> "NumberSetting":
        """Must be implemented by child."""

    @abstractmethod
    def __imul__(self, value: NumberStr) -> "NumberSetting":
        """Must be implemented by child."""


class IntSetting(NumberSetting):
    """Stores an integer setting."""

    def override(self, new_value: NumberStr) -> None:
        ivalue = self.convert(new_value)
        self._value = clamp(ivalue, self.min_value, self.max_value)

    @ensure_type(int)
    def convert(self, text: str) -> int:
        return int(text)

    def __iadd__(self, value: NumberStr) -> "IntSetting":
        """Add a value to the currently stored integer.

        Args:
            value: The integer value to add as string.
        """
        ivalue = self.convert(value)
        self._value = clamp(self._value + ivalue, self.min_value, self.max_value)
        return self

    def __imul__(self, value: NumberStr) -> "IntSetting":
        """Multiply the currently stored integer with a value.

        Args:
            value: The value to multiply with as string.
        """
        ivalue = self.convert(value)
        self._value = clamp(self._value * ivalue, self.min_value, self.max_value)
        return self

    def __str__(self) -> str:
        return "Integer"


class FloatSetting(NumberSetting):
    """Stores a float setting."""

    def override(self, new_value: NumberStr) -> None:
        fvalue = self.convert(new_value)
        self._value = clamp(fvalue, self.min_value, self.max_value)

    @ensure_type(float, int)
    def convert(self, text: str) -> float:
        return float(text)

    def __iadd__(self, value: NumberStr) -> "FloatSetting":
        """Add a value to the currently stored float.

        Args:
            value: The float value to add as string.
        """
        fvalue = self.convert(value)
        self._value = clamp(self._value + fvalue, self.min_value, self.max_value)
        return self

    def __imul__(self, value: NumberStr) -> "FloatSetting":
        """Multiply the currently stored float with a value.

        Args:
            value: The value to multiply with as string.
        """
        fvalue = self.convert(value)
        self._value = clamp(self._value * fvalue, self.min_value, self.max_value)
        return self

    def __str__(self) -> str:
        return "Float"


class ThumbnailSizeSetting(Setting):
    """Stores a thumbnail size setting.

    This setting is stored as integer value which must be one of 64, 128, 256,
    512.
    """

    ALLOWED_VALUES = 64, 128, 256, 512

    def override(self, new_value: IntStr) -> None:
        """Override the setting with a new thumbnail size.

        Args:
            new_value: String containing.
        """
        ivalue = self.convert(new_value)
        if ivalue not in self.ALLOWED_VALUES:
            raise ValueError("Thumbnail size must be one of 64, 128, 256, 512")
        self._value = ivalue

    @ensure_type(int)
    def convert(self, value: IntStr) -> int:
        return int(value)

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
        self._value = self.convert(new_value)

    @ensure_type(str)
    def convert(self, value: str) -> str:
        return str(value)

    def __str__(self) -> str:
        return "String"


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
    hidden=True,
)
STYLE = StrSetting("style", "default", hidden=True)
COMMAND_HISTORY_LIMIT = IntSetting(
    "history_limit",
    100,
    desc="Maximum number of commands to store in history",
    hidden=True,
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
