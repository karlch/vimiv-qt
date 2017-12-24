# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Handles key and mouse events."""

import collections
import string

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QKeySequence

from vimiv.commands import runners
from vimiv.config import keybindings
from vimiv.modes import modehandler


class CountHandler(QTimer):
    """Store and receive digits given by keypress.

    Attributes:
        _count: String containing all currently stored digits.
    """

    def __init__(self):
        super().__init__()
        self._count = ""
        self.setSingleShot(True)
        self.setInterval(2000)
        self.timeout.connect(self._clear_count)

    def add_count(self, digit):
        """Add one digit to the storage."""
        self._count += digit
        if self.isActive():  # Reset timeout when adding more digits
            self.stop()
        self.start()

    def get_count(self):
        """Receive the currently stored digits and clear storage."""
        count = self._count
        self._clear_count()
        return count

    def _clear_count(self):
        self._count = ""


class PartialMatchHandler(QTimer):
    """Store and receive keynames that match a binding partially.

    Attributes:
        _keys: String containing all currently stored keynames.
    """

    def __init__(self):
        super().__init__()
        self._keys = ""
        self.setSingleShot(True)
        self.setInterval(2000)
        self.timeout.connect(self.clear_keys)

    def add_key(self, key):
        """Add one key to the storage."""
        self._keys += key
        if self.isActive():  # Reset timeout when adding more keys
            self.stop()
        self.start()

    def get_keys(self):
        """Receive the currently stored keys and clear storage."""
        keys = self._keys
        self.clear_keys()
        return keys

    def clear_keys(self):
        """Clear keys on timeout."""
        self._keys = ""


class KeyHandler():
    """Deal with keyPressEvent events for gui widgets.

    This class is used by gui classes as first parent, second being some
    QWidget, to handle the keyPressEvent slot.

    Class Attributes:
        count_handler: CountHandler object to store and receive digits.
        partial_handler: PartialMatchHandler object to store and receive
            partially matching keys.
        runner: Runner for internal commands to run the bound commands.
    """

    count_handler = CountHandler()
    partial_handler = PartialMatchHandler()
    runner = runners.CommandRunner()

    def keyPressEvent(self, event):
        """Handle key press event for the widget.

        Args:
            event: QKeyEvent that activated the keyPressEvent.
        """
        mode = modehandler.current().lower()
        keyname = self.partial_handler.get_keys() + keyevent_to_string(event)
        bindings = keybindings.get(mode)
        # Count
        if keyname and keyname in string.digits:
            self.count_handler.add_count(keyname)
            if mode == "command":  # Enter digits in command line
                # super() is the parent Qt widget
                super().keyPressEvent(event)  # pylint: disable=no-member
        # Complete match => run command
        elif keyname and keyname in bindings:
            count = self.count_handler.get_count()
            cmd = bindings[keyname]
            self.runner(count + cmd, mode)
        # Partial match => store keys
        elif bindings.partial_match(keyname):
            self.partial_handler.add_key(keyname)
        # Nothing => run default Qt bindings of parent object
        else:
            # super() is the parent Qt widget
            super().keyPressEvent(event)  # pylint: disable=no-member


def on_mouse_click(event):
    raise NotImplementedError


def keyevent_to_string(event):
    """Convert QKeyEvent to meaningful string.

    This gets the name of the main key and adds pressed modifiers via Mod+.

    Args:
        event: The emitted QKeyEvent.
    Return:
        Name of the key pressed as meaningful string.
    """
    # Parse modifiers
    modmask2str = collections.OrderedDict([
        (Qt.ControlModifier, "ctrl"),
        (Qt.AltModifier, "alt"),
        (Qt.MetaModifier, "meta"),
    ])
    modifiers = (Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta,
                 Qt.Key_AltGr, Qt.Key_Super_L, Qt.Key_Super_R, Qt.Key_Hyper_L,
                 Qt.Key_Hyper_R, Qt.Key_Direction_L, Qt.Key_Direction_R)
    if event.key() in modifiers:
        # Only modifier pressed
        return ""
    mod = event.modifiers()
    parts = []
    for mask, mod_name in modmask2str.items():
        if mod & mask and mod_name not in parts:
            parts.append(mod_name)
    # Append keyname
    parts.append(_get_keyname(event))
    keyname = "+".join(parts)
    return keyname


def _get_keyname(event):
    """Get main keyname of QKeyEvent.

    Converts special keys to usable names and uses event.text() otherwise.

    Args:
        event: The emitted QKeyEvent.
    Return:
        Name of the main key press escaping special keys.
    """
    special_keys = {
        Qt.Key_Space: "space",
        Qt.Key_Backtab: "tab",
        Qt.Key_Tab: "tab",
        Qt.Key_Escape: "escape",
        Qt.Key_Enter: "enter",
        Qt.Key_Return: "return",
        Qt.Key_Backspace: "backspace",
        Qt.Key_Left: "left",
        Qt.Key_Right: "right",
        Qt.Key_Up: "up",
        Qt.Key_Down: "down",
        Qt.Key_Home: "home",
        Qt.Key_End: "end",
    }
    if event.key() in special_keys:
        # Parse shift here as the key does not support it otherwise
        text = special_keys[event.key()]
        if event.modifiers() & Qt.ShiftModifier:
            text = "shift+" + text
        return text
    if event.key() == Qt.Key_Colon:  # Required as : is the separator
        return "colon"
    if event.text().isprintable():
        return event.text()
    return QKeySequence(event.key()).toString().lower()
