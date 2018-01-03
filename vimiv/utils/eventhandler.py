# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Handles key and mouse events."""

import collections
import string

from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSlot
from PyQt5.QtGui import QKeySequence

from vimiv.commands import commands, cmdrunner
from vimiv.config import keybindings
from vimiv.gui import statusbar
from vimiv.modes import modehandler
from vimiv.utils import objreg


def init():
    """Create objects needed by the event handler class."""
    PartialHandler()


class TempKeyStorage(QTimer):
    """Storage to store and get keynames until timeout.

    Attributes:
        text: Currently stored keynames.
    """

    def __init__(self):
        super().__init__()
        self.setSingleShot(True)
        self.setInterval(2000)
        self.text = ""
        self.timeout.connect(self.clear_text)

    def add_text(self, text):
        """Add text to storage."""
        self.text += text
        if self.isActive():  # Reset timeout
            self.stop()
        self.start()
        statusbar.update()

    def get_text(self):
        """Get text from storage."""
        text = self.text
        self.clear_text()
        return text

    @pyqtSlot()
    def clear_text(self):
        """Clear storage."""
        self.stop()  # Can be called from get_text on keyPressEvent
        self.text = ""
        statusbar.update()


class PartialHandler(QObject):
    """Handle partial matches and counts for KeyHandler.

    Attributes:
        count: TempKeyStorage for counts.
        keys: TempKeyStorage for partially matched keys.
    """

    @objreg.register("partialkeys")
    def __init__(self):
        super().__init__()
        self.count = TempKeyStorage()
        self.keys = TempKeyStorage()

    @keybindings.add("<escape>", "clear-keys")
    @commands.register(instance="partialkeys", hide=True)
    def clear_keys(self):
        """Clear count and partially matched keys."""
        self.count.clear_text()
        self.keys.clear_text()
        statusbar.update()

    @statusbar.module("{keys}", instance="partialkeys")
    def get_keys(self):
        return self.count.text + self.keys.text


class KeyHandler():
    """Deal with keyPressEvent events for gui widgets.

    This class is used by gui classes as first parent, second being some
    QWidget, to handle the keyPressEvent slot.
    """

    def keyPressEvent(self, event):
        """Handle key press event for the widget.

        Args:
            event: QKeyEvent that activated the keyPressEvent.
        """
        mode = modehandler.current()
        partial_handler = objreg.get("partialkeys")
        stored_keys = partial_handler.keys.get_text()
        keyname = keyevent_to_string(event)
        bindings = keybindings.get(mode)
        # Prefer clear-keys
        if keyname in bindings and bindings[keyname] == "clear-keys":
            cmdrunner.run("clear-keys", mode)
            return
        keyname = stored_keys + keyname
        # Count
        if keyname and keyname in string.digits and mode != "command":
            partial_handler.count.add_text(keyname)
        # Complete match => run command
        elif keyname and keyname in bindings:
            count = partial_handler.count.get_text()
            cmd = bindings[keyname]
            cmdrunner.run(count + cmd, mode)
        # Partial match => store keys
        elif bindings.partial_match(keyname):
            partial_handler.keys.add_text(keyname)
        # Nothing => run default Qt bindings of parent object
        else:
            # super() is the parent Qt widget
            super().keyPressEvent(event)  # pylint: disable=no-member
            statusbar.update()  # Will not be called by command


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
        (Qt.ControlModifier, "<ctrl>"),
        (Qt.AltModifier, "<alt>"),
        (Qt.MetaModifier, "<meta>"),
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
    keyname = "".join(parts)
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
