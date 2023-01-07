# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.gui.eventhandler."""

import pytest

from vimiv.qt.core import QEvent, Qt, QPointF
from vimiv.qt.gui import QKeyEvent, QMouseEvent

from vimiv.gui import eventhandler


@pytest.fixture()
def storage(qtbot):
    yield eventhandler.TempKeyStorage()


def test_temp_key_storage_add_keys(storage):
    storage.add_keys("a")
    storage.add_keys("1")
    assert storage.text == "a1"


def test_temp_key_storage_get_keys(storage):
    keys = ("a", "1")
    for key in keys:
        storage.add_keys(key)
    assert storage.get_keys() == keys
    assert not storage.text  # Getting should clear


def test_temp_key_storage_clears_text(storage, qtbot):
    storage.setInterval(1)  # We do not want to wait 2s in test
    with qtbot.waitSignal(storage.timeout, timeout=5):
        storage.add_keys("g")
    assert storage.get_text() == ""


@pytest.mark.parametrize(
    "qtkey, modifier, keyname, expected",
    [
        (Qt.Key.Key_A, Qt.KeyboardModifier.NoModifier, "a", ("a",)),
        (Qt.Key.Key_A, Qt.KeyboardModifier.ShiftModifier, "A", ("A",)),
        (Qt.Key.Key_Tab, Qt.KeyboardModifier.NoModifier, "\t", ("<tab>",)),
        (Qt.Key.Key_Tab, Qt.KeyboardModifier.ShiftModifier, "\t", ("<shift>", "<tab>")),
        (Qt.Key.Key_A, Qt.KeyboardModifier.ControlModifier, "a", ("<ctrl>", "a")),
        (Qt.Key.Key_A, Qt.KeyboardModifier.AltModifier, "a", ("<alt>", "a")),
        (
            Qt.Key.Key_A,
            Qt.KeyboardModifier.AltModifier | Qt.KeyboardModifier.ControlModifier,
            "a",
            ("<ctrl>", "<alt>", "a"),
        ),
        (Qt.Key.Key_Colon, Qt.KeyboardModifier.NoModifier, ":", ("<colon>",)),
        (Qt.Key.Key_Equal, Qt.KeyboardModifier.NoModifier, "=", ("<equal>",)),
    ],
)
def test_keyevent_to_sequence(qtkey, modifier, keyname, expected):
    event = QKeyEvent(QEvent.Type.KeyPress, qtkey, modifier, keyname)
    assert eventhandler.keyevent_to_sequence(event) == expected


def test_keyevent_to_sequence_for_only_modifier():
    with pytest.raises(ValueError):
        event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_Shift,
            Qt.KeyboardModifier.ShiftModifier,
            "",
        )
        assert eventhandler.keyevent_to_sequence(event) == tuple()


@pytest.mark.parametrize(
    "qtbutton, modifier, expected",
    [
        (Qt.MouseButton.LeftButton, Qt.KeyboardModifier.NoModifier, ("<button-left>",)),
        (
            Qt.MouseButton.MiddleButton,
            Qt.KeyboardModifier.NoModifier,
            ("<button-middle>",),
        ),
        (
            Qt.MouseButton.RightButton,
            Qt.KeyboardModifier.NoModifier,
            ("<button-right>",),
        ),
        (
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.ControlModifier,
            (
                "<ctrl>",
                "<button-left>",
            ),
        ),
    ],
)
def test_mouse_event_to_sequence(qtbutton, modifier, expected):
    event = _create_mouse_event(qtbutton, modifier=modifier)
    assert eventhandler.mouseevent_to_sequence(event) == expected


def _create_mouse_event(button, modifier=Qt.KeyboardModifier.NoModifier):
    return QMouseEvent(
        QEvent.Type.MouseButtonPress,
        QPointF(0, 0),
        QPointF(0, 0),
        button,
        button,
        modifier,
    )
