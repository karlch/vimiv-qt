# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.utils.eventhandler."""

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QKeyEvent

from vimiv.utils import eventhandler


def test_count_handler_add_and_get_count(qtbot):
    count_handler = eventhandler.CountHandler()
    qtbot.addWidget(count_handler)
    count_handler.add_count("2")
    count_handler.add_count("3")
    assert count_handler.get_count() == "23"


def test_count_handler_clears_count(qtbot):
    count_handler = eventhandler.CountHandler()
    count_handler.setInterval(1)  # We do not want to wait 2s in test
    qtbot.addWidget(count_handler)
    with qtbot.waitSignal(count_handler.timeout, timeout=5):
        count_handler.add_count("2")
    assert count_handler.get_count() == ""


def test_keyevent_to_string_for_lowercase_letter():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.NoModifier, "a")
    assert eventhandler.keyevent_to_string(event) == "a"


def test_keyevent_to_string_for_uppercase_letter():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.ShiftModifier, "A")
    assert eventhandler.keyevent_to_string(event) == "A"


def test_keyevent_to_string_for_special_key():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.NoModifier, "\t")
    assert eventhandler.keyevent_to_string(event) == "tab"


def test_keyevent_to_string_for_special_key_with_shift():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Tab, Qt.ShiftModifier, "\t")
    assert eventhandler.keyevent_to_string(event) == "shift+tab"


def test_keyevent_to_string_for_control_modifier_and_letter():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.ControlModifier, "a")
    assert eventhandler.keyevent_to_string(event) == "ctrl+a"


def test_keyevent_to_string_for_alt_modifier_and_letter():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_A, Qt.AltModifier, "a")
    assert eventhandler.keyevent_to_string(event) == "alt+a"


def test_keyevent_to_string_for_only_modifier():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Shift, Qt.ShiftModifier, "")
    assert eventhandler.keyevent_to_string(event) is None


def test_keyevent_to_string_for_colon():
    event = QKeyEvent(QEvent.KeyPress, Qt.Key_Colon, Qt.NoModifier, ":")
    assert eventhandler.keyevent_to_string(event) == "colon"
