# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.gui.eventhandler."""

import pytest

from vimiv.qt.core import QEvent, Qt, QPoint
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
        (Qt.Key_A, Qt.NoModifier, "a", ("a",)),
        (Qt.Key_A, Qt.ShiftModifier, "A", ("A",)),
        (Qt.Key_Tab, Qt.NoModifier, "\t", ("<tab>",)),
        (Qt.Key_Tab, Qt.ShiftModifier, "\t", ("<shift>", "<tab>")),
        (Qt.Key_A, Qt.ControlModifier, "a", ("<ctrl>", "a")),
        (Qt.Key_A, Qt.AltModifier, "a", ("<alt>", "a")),
        (Qt.Key_A, Qt.AltModifier | Qt.ControlModifier, "a", ("<ctrl>", "<alt>", "a")),
        (Qt.Key_Colon, Qt.NoModifier, ":", ("<colon>",)),
        (Qt.Key_Equal, Qt.NoModifier, "=", ("<equal>",)),
    ],
)
def test_keyevent_to_sequence(qtkey, modifier, keyname, expected):
    event = QKeyEvent(QEvent.KeyPress, qtkey, modifier, keyname)
    assert eventhandler.keyevent_to_sequence(event) == expected


def test_keyevent_to_sequence_for_only_modifier():
    with pytest.raises(ValueError):
        event = QKeyEvent(QEvent.KeyPress, Qt.Key_Shift, Qt.ShiftModifier, "")
        assert eventhandler.keyevent_to_sequence(event) == tuple()


@pytest.mark.parametrize(
    "qtbutton, modifier, expected",
    [
        (Qt.LeftButton, Qt.NoModifier, ("<button-left>",)),
        (Qt.MiddleButton, Qt.NoModifier, ("<button-middle>",)),
        (Qt.RightButton, Qt.NoModifier, ("<button-right>",)),
        (
            Qt.LeftButton,
            Qt.ControlModifier,
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


def _create_mouse_event(button, modifier=Qt.NoModifier):
    return QMouseEvent(
        QEvent.MouseButtonPress, QPoint(0, 0), QPoint(0, 0), button, button, modifier
    )
