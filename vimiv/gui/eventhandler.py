# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handles key and mouse events."""

import string

from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt5.QtGui import QKeySequence, QKeyEvent

from vimiv import api, utils
from vimiv.commands import runners, search


_logger = utils.log.module_logger(__name__)


class TempKeyStorage(QTimer):
    """Storage to store and get keynames until timeout.

    Attributes:
        text: Currently stored keynames.
    """

    def __init__(self):
        super().__init__()
        self.text = ""

        self.setSingleShot(True)
        self.setInterval(api.settings.keyhint.timeout.value)
        self.timeout.connect(self.on_timeout)
        api.settings.keyhint.timeout.changed.connect(self._on_timeout_changed)

    def add_text(self, text):
        """Add text to storage."""
        self.text += text
        if self.isActive():  # Reset timeout
            self.stop()
        self.start()
        api.status.update("added keys to temporary key storage")

    def get_text(self):
        """Get text from storage."""
        text = self.text
        self.clear_text()
        return text

    def clear_text(self):
        """Clear storage."""
        self.stop()
        self.text = ""

    @utils.slot
    def on_timeout(self):
        """Clear text and update status to remove partial keys from statusbar."""
        self.clear_text()
        api.status.update("timeout keys from temporary key storage")

    def _on_timeout_changed(self, value: int):
        """Update timer interval if the keyhint timeout setting changed."""
        self.setInterval(value)


class PartialHandler(QObject):
    """Handle partial matches and counts for KeyHandler.

    Attributes:
        count: TempKeyStorage for counts.
        keys: TempKeyStorage for partially matched keys.

    Signals:
        partial_matches: Emitted when there are partial matches for a keybinding.
            arg1: Prefix for which partial matches exist.
            arg2: List of partial matches.
        partial_cleared: Emitted when the partial matches are cleared.
    """

    partial_matches = pyqtSignal(str, list)
    partial_cleared = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.count = TempKeyStorage()
        self.keys = TempKeyStorage()
        self.keys.timeout.connect(self.partial_cleared.emit)

    def clear_keys(self):
        """Clear count and partially matched keys."""
        self.count.clear_text()
        self.keys.clear_text()
        self.partial_cleared.emit()

    def get_keys(self):
        return self.count.text + self.keys.text


class KeyHandler:
    """Deal with keyPressEvent events for gui widgets.

    This class is used by gui classes as first parent, second being some
    QWidget, to handle the keyPressEvent slot.
    """

    partial_handler = PartialHandler()

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press event for the widget.

        Args:
            event: QKeyEvent that activated the keyPressEvent.
        """
        mode = api.modes.current()
        try:
            keyname = keyevent_to_string(event)
        except ValueError:  # Only modifier pressed
            _logger.debug("KeyPressEvent: only modifier pressed")
            return
        _logger.debug("KeyPressEvent: handling %s for mode %s", keyname, mode.name)
        bindings = api.keybindings.get(mode)
        # Handle escape separately as it affects multiple widgets and must clear partial
        # matches instead of checking for them
        if keyname == "<escape>" and mode in api.modes.GLOBALS:
            _logger.debug("KeyPressEvent: handling <escape> key specially")
            self.partial_handler.clear_keys()
            search.search.clear()
            api.status.update("escape pressed")
            return
        stored_keys = self.partial_handler.keys.get_text()
        keyname = stored_keys + keyname
        partial_matches = bindings.partial_matches(keyname)
        # Count
        if keyname and keyname in string.digits and mode != api.modes.COMMAND:
            _logger.debug("KeyPressEvent: adding digits")
            self.partial_handler.count.add_text(keyname)
        # Complete match => run command
        elif keyname and keyname in bindings:
            _logger.debug("KeyPressEvent: found command")
            count = self.partial_handler.count.get_text()
            cmd = bindings[keyname]
            runners.run(cmd, count=count, mode=mode)
            self.partial_handler.clear_keys()
        # Partial match => store keys
        elif partial_matches:
            self.partial_handler.keys.add_text(keyname)
            self.partial_handler.partial_matches.emit(keyname, partial_matches)
        # Nothing => run default Qt bindings of parent object
        else:
            # super() is the parent Qt widget
            super().keyPressEvent(event)  # type: ignore  # pylint: disable=no-member
            self.partial_handler.clear_keys()
            api.status.update("regular Qt key event")  # Will not be called by command

    @staticmethod
    @api.status.module("{keys}")
    def unprocessed_keys():
        """Unprocessed keys that were pressed."""
        return KeyHandler.partial_handler.get_keys()


def on_mouse_click(event):
    raise NotImplementedError


def keyevent_to_string(event):
    """Convert QKeyEvent to meaningful string.

    This gets the name of the main key and adds pressed modifiers via Mod+.

    Args:
        event: The emitted QKeyEvent.
    Returns:
        Name of the key pressed as meaningful string.
    """
    # Parse modifiers
    modmask2str = {
        Qt.ControlModifier: "<ctrl>",
        Qt.AltModifier: "<alt>",
        Qt.MetaModifier: "<meta>",
    }
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
    # Prepend all modifiers and append keyname
    mod = event.modifiers()
    modifier_names = [mod_name for mask, mod_name in modmask2str.items() if mod & mask]
    keyname = _get_keyname(event)
    return "".join(modifier_names) + keyname


def _get_keyname(event):
    """Get main keyname of QKeyEvent.

    Converts special keys to usable names and uses event.text() otherwise.

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
        text = special_keys[event.key()]
        if event.modifiers() & Qt.ShiftModifier:
            text = "<shift>" + text
        return text
    if event.key() == Qt.Key_Colon:  # Required as : is the separator
        return "<colon>"
    if event.text().isprintable():
        return event.text()
    return QKeySequence(event.key()).toString().lower()
