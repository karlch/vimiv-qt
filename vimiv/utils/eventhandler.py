# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Handles key and mouse events."""

import collections
import string

from PyQt5.QtCore import Qt, QTimer

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
        self.stop()


class KeyHandler():
    """Deal with keyPressEvent events for gui widgets.

    This class is used by gui classes as first parent, second being some
    QWidget, to handle the keyPressEvent slot.

    Class Attributes:
        count_handler: CountHandler object to store and receive digits.
        runner: Runner for internal commands to run the bound commands.
    """

    count_handler = CountHandler()
    runner = runners.CommandRunner()

    def keyPressEvent(self, event):
        """Handle key press event for the widget.

        Args:
            event: QKeyEvent that activated the keyPressEvent.
        """
        mode = modehandler.current().lower()
        bindings = keybindings.get(mode)
        keyname = keyevent_to_string(event)
        if keyname and keyname in string.digits:
            self.count_handler.add_count(keyname)
            if mode == "command":
                super().keyPressEvent(event)  # Enter digits in command line
        elif keyname and keyname in bindings:
            count = self.count_handler.get_count()
            cmd = bindings[keyname]
            self.runner(count + cmd, mode)
        else:  # Default Qt bindings of parent object
            super().keyPressEvent(event)


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
        return None
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
    return event.text()
