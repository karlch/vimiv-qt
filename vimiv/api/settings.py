# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Store and change settings.

Module attributes:
    _storage: Initialized Storage object to store settings globally.
"""

import enum
from abc import abstractmethod
from contextlib import suppress
from typing import Any, Dict, ItemsView, List, Callable, TypeVar

from PyQt5.QtCore import QObject, pyqtSignal

from vimiv.utils import clamp, AbstractQObjectMeta, log, customtypes
from . import prompt


SettingT = TypeVar("SettingT", bound="Setting")
MethodT = Callable[[SettingT, Any], Any]


_storage: Dict[str, "Setting"] = {}
_logger = log.module_logger(__name__)


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


def reset() -> None:
    """Reset all settings to their default value."""
    for setting in _storage.values():
        setting.set_to_default()


def items() -> ItemsView[str, "Setting"]:
    return _storage.items()


class Setting(QObject, metaclass=AbstractQObjectMeta):
    """Stores a setting and its attributes.

    This class can not be used directly. Instead it is used as BaseClass for
    different types of settings.

    Attributes:
        name: Name of the setting as string.
        desc: Description of the setting.
        hidden: True if the setting should not be visible in the :set completion.

        _default: Default value of the setting stored in its python type.
        _suggestions: List of useful values to show in completion widget.
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

        See the class attributes section for a description of the arguments.
        """
        super().__init__()
        self.name = name
        self.desc = desc
        self.hidden = hidden
        self._value = self._default = default_value
        self._suggestions = suggestions if suggestions is not None else []
        _storage[name] = self  # Store setting in storage

    @property
    @abstractmethod
    def typ(self) -> type:
        """The python type of this setting defined by the child class."""

    @property
    def default(self) -> Any:
        return self._default

    @property
    def value(self) -> Any:
        return self._value

    @value.setter
    def value(self, value: Any) -> Any:
        self._value = self.convert(value)
        _logger.debug("Setting '%s' to '%s'", self.name, value)
        self.changed.emit(self._value)

    def set_to_default(self) -> None:
        self._value = self.default

    def suggestions(self) -> List[str]:
        """Return a list of valid or useful suggestions for the setting.

        Used by the completion widget.
        """
        return self._suggestions

    def convert(self, value: Any) -> Any:
        """Convert value to setting type before using it."""
        with suppress(ValueError):  # We re-raise later with a consistent message
            if isinstance(value, str):
                return self.convertstr(value)
            return self.typ(value)
        raise ValueError(f"Cannot convert '{value}' to {self}")

    def convertstr(self, value: str) -> Any:
        return self.typ(value)


class BoolSetting(Setting):
    """Stores a boolean setting."""

    typ = bool

    def toggle(self) -> None:
        self.value = not self.value

    def suggestions(self) -> List[str]:
        return ["True", "False"]

    def convertstr(self, text: str) -> bool:
        text = text.lower()
        if text in ("yes", "true", "1"):
            return True
        if text in ("no", "false", "0"):
            return False
        raise ValueError

    def __str__(self) -> str:
        return "Bool"

    def __bool__(self) -> bool:
        return self.value


class PromptSetting(Setting):
    """Stores a boolean setting with the additional ask option.

    When the value of this setting is ask, the user is prompted everytime the boolean
    state of this setting is requested.

    Attributes:
        _title: Title of the question the user is prompted with.
        _question: Actual question the user is prompted with.
    """

    class Options(enum.Enum):
        """Enum of valid options for this setting."""

        true = "true"
        false = "false"
        ask = "ask"

        def __str__(self) -> str:
            return self.value

    typ = Options

    def __init__(
        self, *args: Any, question_title: str, question_body: str, **kwargs: Any
    ):
        super().__init__(*args, **kwargs)
        self._title = question_title
        self._question = question_body

    def suggestions(self) -> List[str]:
        return ["true", "prompt", "false"]

    def convertstr(self, text: str) -> "PromptSetting.Options":
        text = text.lower()
        if text in ("yes", "1"):
            return self.Options.true
        if text in ("no", "0"):
            return self.Options.false
        return self.Options(text)

    def __str__(self) -> str:
        return "Prompt"

    def __bool__(self) -> bool:
        if self.value == self.Options.ask:
            return bool(prompt.ask_question(title=self._title, body=self._question))
        if self.value == self.Options.false:
            return False
        return True


class NumberSetting(Setting):  # pylint: disable=abstract-method  # Still abstract class
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
        default_value: customtypes.Number,
        desc: str = "",
        suggestions: List[str] = None,
        hidden: bool = False,
        min_value: customtypes.Number = None,
        max_value: customtypes.Number = None,
    ):
        """Additionally allow setting minimum and maximum value."""
        super().__init__(name, default_value, desc, suggestions, hidden=hidden)
        self.min_value = min_value
        self.max_value = max_value

    def __iadd__(self, value: customtypes.NumberStr) -> "NumberSetting":
        """Add a value to the currently stored number."""
        self.value += super().convert(value)
        return self

    def __imul__(self, value: customtypes.NumberStr) -> "NumberSetting":
        """Multiply the currently stored number with a value."""
        self.value *= super().convert(value)
        return self

    def convert(self, value: customtypes.NumberStr) -> customtypes.Number:
        return clamp(super().convert(value), self.min_value, self.max_value)


class IntSetting(NumberSetting):
    """Stores an integer setting."""

    typ = int

    def __str__(self) -> str:
        return "Integer"


class FloatSetting(NumberSetting):
    """Stores a float setting."""

    typ = float

    def __str__(self) -> str:
        return "Float"


class ThumbnailSizeSetting(Setting):
    """Stores a thumbnail size setting.

    This setting is stored as integer value which must be one of 64, 128, 256,
    512.
    """

    typ = int
    ALLOWED_VALUES = 64, 128, 256, 512

    def convert(self, value: customtypes.IntStr) -> int:
        ivalue = super().convert(value)
        if ivalue not in self.ALLOWED_VALUES:
            raise ValueError("Thumbnail size must be one of 64, 128, 256, 512")
        return ivalue

    def step(self, up: bool = True) -> None:
        """Change thumbnail size by one step up if up else down."""
        index = self.ALLOWED_VALUES.index(self.value) + (1 if up else -1)
        index = clamp(index, 0, len(self.ALLOWED_VALUES) - 1)
        self.value = self.ALLOWED_VALUES[index]

    def suggestions(self) -> List[str]:
        return [str(value) for value in self.ALLOWED_VALUES]

    def __str__(self) -> str:
        return "ThumbSize"


class StrSetting(Setting):
    """Stores a string setting."""

    typ = str

    def __str__(self) -> str:
        return "String"


# Initialize all settings

monitor_fs = BoolSetting(
    "monitor_filesystem",
    True,
    desc="Monitor current directory for changes and reload widgets automatically",
)
shuffle = BoolSetting("shuffle", False, desc="Randomly shuffle images")
startup_library = BoolSetting(
    "startup_library",
    True,
    desc="Enter library at startup if there are no images to show",
    hidden=True,
)
style = StrSetting("style", "default", hidden=True)


class command:  # pylint: disable=invalid-name
    """Namespace for command related settings."""

    history_limit = IntSetting(
        "command.history_limit",
        100,
        desc="Maximum number of commands to store in history",
        hidden=True,
    )


class completion:  # pylint: disable=invalid-name
    """Namespace for completion related settings."""

    fuzzy = BoolSetting(
        "completion.fuzzy", False, desc="Use fuzzy matching in completion"
    )


class search:  # pylint: disable=invalid-name
    """Namespace for search related settings."""

    ignore_case = BoolSetting(
        "search.ignore_case",
        True,
        desc="Ignore case when searching, i.e. 'A' and 'a' are equal",
    )
    incremental = BoolSetting(
        "search.incremental",
        True,
        desc="Automatically filter search results when typing",
    )


class image:  # pylint: disable=invalid-name
    """Namespace for image related settings."""

    autoplay = BoolSetting(
        "image.autoplay", True, desc="Start playing animations on open"
    )
    autowrite = PromptSetting(
        "image.autowrite",
        PromptSetting.Options.ask,
        question_title="Image edited",
        question_body="Do you want to write your changes to disk?",
        desc="Save images on changes",
    )
    overzoom = FloatSetting(
        "image.overzoom",
        1.0,
        desc="Maximum scale to apply trying to fit image to window",
        suggestions=["1.0", "1.5", "2.0", "5.0"],
        min_value=1.0,
    )


class library:  # pylint: disable=invalid-name
    """Namespace for library related settings."""

    width = FloatSetting(
        "library.width",
        0.3,
        desc="Width of the library as fraction of main window size",
        suggestions=["0.2", "0.3", "0.4", "0.5"],
        min_value=0.05,
        max_value=0.95,
    )
    show_hidden = BoolSetting(
        "library.show_hidden", False, desc="Show hidden files in the library"
    )


class thumbnail:  # pylint: disable=invalid-name
    """Namespace for thumbnail related settings."""

    size = ThumbnailSizeSetting("thumbnail.size", 128, desc="Size of thumbnails")


class slideshow:  # pylint: disable=invalid-name
    """Namespace for slideshow related settings."""

    delay = FloatSetting(
        "slideshow.delay", 2.0, desc="Delay to next image in slideshow", min_value=0.5
    )
    indicator = StrSetting(
        "slideshow.indicator",
        "slideshow:",
        desc="Text to display in statusbar when slideshow is running",
    )


class statusbar:  # pylint: disable=invalid-name
    """Namespace for statusbar related settings."""

    collapse_home = BoolSetting(
        "statusbar.collapse_home", True, desc="Collapse /home/user to ~ in statusbar"
    )
    show = BoolSetting("statusbar.show", True, desc="Always display the statusbar")
    message_timeout = IntSetting(
        "statusbar.message_timeout",
        60000,
        desc="Time in ms until statusbar messages are removed",
        min_value=500,
    )
    mark_indicator = StrSetting(
        "statusbar.mark_indicator",
        "<b>*</b>",
        desc="Text to display if the current image is marked",
    )
    # Statusbar module strings, these are not retrieved by their type
    StrSetting("statusbar.left", "{pwd}")
    StrSetting("statusbar.left_image", "{index}/{total} {basename} [{zoomlevel}]")
    StrSetting(
        "statusbar.left_thumbnail",
        "{thumbnail-index}/{thumbnail-total} {thumbnail-name}",
    )
    StrSetting(
        "statusbar.left_manipulate",
        "{basename}   {image-size}   Modified: {modified}   {processing}",
    )
    StrSetting("statusbar.center_thumbnail", "{thumbnail-size}")
    StrSetting(
        "statusbar.center",
        "{slideshow-indicator} {slideshow-delay} {transformation-info}",
    )
    StrSetting("statusbar.right", "{keys}  {mark-count}  {mode}")
    StrSetting("statusbar.right_image", "{keys}  {mark-indicator} {mark-count}  {mode}")


class keyhint:  # pylint: disable=invalid-name
    """Namespace for keyhint related settings."""

    delay = IntSetting(
        "keyhint.delay",
        500,
        desc="Delay (in ms) until the keyhint widget is displayed",
        min_value=0,
    )
    timeout = IntSetting(
        "keyhint.timeout",
        5000,
        desc="Time (in ms) after which partially typed keybindings are cleared",
        min_value=100,
    )


class title:  # pylint: disable=invalid-name
    """Namespace for title related settings."""

    # Title module strings, these are not retrieved by their type
    StrSetting(
        "title.fallback",
        "vimiv",
        desc="Default window title if no mode specific options exist",
    )
    StrSetting("title.image", "vimiv - {basename}", desc="Window title in image mode")
