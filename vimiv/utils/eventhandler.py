# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Handles key and mouse events."""

import collections

from PyQt5.QtCore import Qt


from vimiv.commands import commands
from vimiv.config import keybindings


def on_key_press(mode):
    """Decorator to handle keyPressEvent.

    Gets the stored keybindings for the corresponding mode and converts the
    event to a meaningful keyname. If the keyname is in the stored bindings,
    the corresponding command is called.

    Args:
        mode: The mode to check for keybindings.
    """
    def decorator(key_press_event):
        """Decorator around the widgets keyPressEvent method."""
        def inner(obj, event):
            """Inner of the decorator.

            Args:
                obj: Corresponds to self in keyPressEvent.
                event: The emitted QKeyEvent.
            """
            bindings = keybindings.get(mode)
            keyname = keyevent_to_string(event)
            if keyname in bindings:
                cmd = bindings[keyname]
                commands.run(cmd, mode)
            else:  # Allow default bindings
                return key_press_event(obj, event)
        return inner
    return decorator


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
