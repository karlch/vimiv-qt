# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handles key and mouse events."""

import string
from typing import Union, Tuple, List, cast

from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QKeySequence, QKeyEvent, QMouseEvent

from vimiv import api, utils
from vimiv.commands import runners, search


SequenceT = Tuple[str, ...]

_logger = utils.log.module_logger(__name__)


class TempKeyStorage(QTimer):
    """Storage to store and get keynames until timeout.

    Attributes:
        text: Currently stored keynames.
    """

    def __init__(self):
        super().__init__()
        self._keys = []

        self.setSingleShot(True)
        self.setInterval(api.settings.keyhint.timeout.value)
        self.timeout.connect(self.on_timeout)
        api.settings.keyhint.timeout.changed.connect(self._on_timeout_changed)

    @property
    def text(self):
        return "".join(self._keys)

    def add_keys(self, *keys):
        """Add text to storage."""
        self._keys.extend(keys)
        if self.isActive():  # Reset timeout
            self.stop()
        self.start()
        api.status.update("added keys to temporary key storage")

    def get_text(self):
        """Get text from storage."""
        return "".join(self.get_keys())

    def get_keys(self):
        """Get tuple of keys from storage."""
        keys = tuple(self._keys)
        self.clear()
        return keys

    def clear(self):
        """Clear storage."""
        self.stop()
        self._keys.clear()

    @utils.slot
    def on_timeout(self):
        """Clear text and update status to remove partial keys from statusbar."""
        self.clear()
        api.status.update("timeout keys from temporary key storage")

    def _on_timeout_changed(self, value: int):
        """Update timer interval if the keyhint timeout setting changed."""
        self.setInterval(value)


class PartialHandler(QObject):
    """Handle partial matches and counts for EventHandlerMixin.

    Attributes:
        count: TempKeyStorage for counts.
        keys: TempKeyStorage for partially matched keys.

    Signals:
        partial_matches: Emitted when there are partial matches for a keybinding.
            arg1: Prefix for which partial matches exist.
            arg2: Iterable of partial matches.
        partial_cleared: Emitted when the partial matches are cleared.
    """

    partial_matches = pyqtSignal(str, object)
    partial_cleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.count = TempKeyStorage()
        self.keys = TempKeyStorage()
        self.keys.timeout.connect(self.partial_cleared.emit)

    def clear_keys(self):
        """Clear count and partially matched keys."""
        self.count.clear()
        self.keys.clear()
        self.partial_cleared.emit()

    @property
    def text(self):
        return self.count.text + self.keys.text


class EventHandlerMixin:
    """Mixing to handle key and mouse events for gui widgets.

    This class is used by gui classes as first parent, second being some
    QWidget, to handle the various input related event slots.
    """

    partial_handler = PartialHandler()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press event for the widget."""
        api.status.clear("KeyPressEvent")
        try:
            keysequence = keyevent_to_sequence(event)
        except ValueError:  # Only modifier pressed
            _logger.debug("KeyPressEvent: only modifier pressed")
            return
        mode = api.modes.current()
        keyname = "".join(keysequence)
        # Handle escape separately as it affects multiple widgets and must clear partial
        # matches instead of checking for them
        if keyname == "<escape>" and mode in api.modes.GLOBALS:
            _logger.debug("KeyPressEvent: handling <escape> key specially")
            self.partial_handler.clear_keys()
            search.search.clear()
            api.status.update("escape pressed")
        # Count
        elif keyname and keyname in string.digits and mode != api.modes.COMMAND:
            _logger.debug("KeyPressEvent: adding digits to count")
            self.partial_handler.count.add_keys(keyname)
        elif not self._process_event(keysequence, mode=mode):
            super().keyPressEvent(event)  # type: ignore

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press event for the widget."""
        api.status.clear("MousePressEvent")
        if not self._process_event(mouseevent_to_sequence(event)):
            super().mousePressEvent(event)  # type: ignore

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Handle mouse press event for the widget."""
        api.status.clear("MouseDoubleClickEvent")
        if not self._process_event(
            mouseevent_to_sequence(event, prefix="double-button")
        ):
            super().mouseDoubleClickEvent(event)  # type: ignore

    def _process_event(self, sequence: SequenceT, mode: api.modes.Mode = None) -> bool:
        """Process event by name.

        Try to (partially) match the name with the current bindings. If a complete match
        is found, the corresponding command is run. Partial matches are displayed and
        the corresponding keys are stored. In case there is no match, reset and return
        False.

        Args:
            sequence: Event keys/buttons as meaningful string sequence.
            mode: Mode in which the event was received. None for current mode.
        Returns:
            True if processing was successful, False otherwise.
        """
        mode = api.modes.current() if mode is None else mode
        name = "".join(sequence)
        _logger.debug("EventHandlerMixin: handling %s for mode %s", name, mode.name)
        bindings = api.keybindings.get(mode)
        stored_keys = self.partial_handler.keys.get_keys()
        match = bindings.match((*stored_keys, *sequence))
        # Complete match => run command
        if match.is_full_match:
            _logger.debug("EventHandlerMixin: found command for event")
            count = self.partial_handler.count.get_text()
            command = cast(str, match.value)  # Would not be a full match otherwise
            runners.run(command, count=count, mode=mode)
            self.partial_handler.clear_keys()
            return True
        # Partial match => store keys
        if match.is_partial_match:
            _logger.debug("EventHandlerMixin: event matches bindings partially")
            self.partial_handler.keys.add_keys(*sequence)
            self.partial_handler.partial_matches.emit(name, match.partial)
            return True
        # Nothing => reset and return False
        _logger.debug("EventHandlerMixin: no matches for event")
        api.status.update("regular Qt event")  # Will not be called by command
        self.partial_handler.clear_keys()
        return False

    @staticmethod
    @api.status.module("{keys}")
    def unprocessed_keys():
        """Unprocessed keys that were pressed."""
        return EventHandlerMixin.partial_handler.text


def keyevent_to_sequence(event: QKeyEvent) -> SequenceT:
    """Convert QKeyEvent to meaningful string sequence."""
    modifiers = (
        Qt.Key_Control,
        Qt.Key_Alt,
        Qt.Key_Shift,
        Qt.Key_Meta,
        Qt.Key_AltGr,
        Qt.Key_Super_L,
        Qt.Key_Super_R,
        Qt.Key_Hyper_L,
        Qt.Key_Hyper_R,
        Qt.Key_Direction_L,
        Qt.Key_Direction_R,
    )
    if event.key() in modifiers:  # Only modifier pressed
        raise ValueError("Modifiers do not have a stand-alone name")
    return (*_get_modifier_names(event), *_get_base_keysequence(event))


def mouseevent_to_sequence(event: QMouseEvent, prefix: str = "button") -> SequenceT:
    """Convert QMouseEvent to meaningful string sequence."""
    button_names = {
        Qt.LeftButton: "left",
        Qt.MiddleButton: "middle",
        Qt.RightButton: "right",
        Qt.BackButton: "back",
        Qt.ForwardButton: "forward",
    }
    button = event.button()
    button_name = button_names[button] if button in button_names else str(button)
    return (*_get_modifier_names(event), f"<{prefix}-{button_name}>")


def _get_modifier_names(event: Union[QKeyEvent, QMouseEvent]) -> List[str]:
    """Return the names of all modifiers pressed in the event."""
    modmask2str = {
        Qt.ControlModifier: "<ctrl>",
        Qt.AltModifier: "<alt>",
        Qt.MetaModifier: "<meta>",
    }
    modifiers = event.modifiers()
    return [
        mod_name
        for mask, mod_name in modmask2str.items()
        if modifiers & mask  # type: ignore
    ]


def _get_base_keysequence(event: QKeyEvent) -> SequenceT:
    """Get main keyname part of QKeyEvent.

    Converts special keys to usable names and uses event.text() otherwise. Is a sequence
    to allow prepending <shift> to special keys.

    Args:
        event: The emitted QKeyEvent.
    Returns:
        Name of the main key press escaping special keys.
    """
    special_keys = {
        Qt.Key_Space: "<space>",
        Qt.Key_Backtab: "<tab>",
        Qt.Key_Tab: "<tab>",
        Qt.Key_Escape: "<escape>",
        Qt.Key_Enter: "<enter>",
        Qt.Key_Return: "<return>",
        Qt.Key_Backspace: "<backspace>",
        Qt.Key_Left: "<left>",
        Qt.Key_Right: "<right>",
        Qt.Key_Up: "<up>",
        Qt.Key_Down: "<down>",
        Qt.Key_Home: "<home>",
        Qt.Key_End: "<end>",
        Qt.Key_PageUp: "<page-up>",
        Qt.Key_PageDown: "<page-down>",
        Qt.Key_Home: "<home>",
        Qt.Key_End: "<end>",
    }
    if event.key() in special_keys:
        # Parse shift here as the key does not support it otherwise
        text = special_keys[event.key()]  # type: ignore
        if event.modifiers() & Qt.ShiftModifier:  # type: ignore
            return "<shift>", text
        return (text,)
    if event.key() == Qt.Key_Colon:  # Required as : is the separator
        return ("<colon>",)
    if event.text().isprintable():
        return (event.text(),)
    return (QKeySequence(event.key()).toString().lower(),)
