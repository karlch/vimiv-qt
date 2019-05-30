# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils"""

import inspect
import pytest
from PyQt5.QtCore import pyqtSignal, QObject

from vimiv import utils


def test_add_html():
    assert utils.add_html("b", "hello") == "<b>hello</b>"


def test_strip_html():
    assert utils.strip_html("<b>hello</b>") == "hello"


def test_clamp_with_min_and_max():
    assert utils.clamp(2, 0, 5) == 2
    assert utils.clamp(2, 3, 5) == 3
    assert utils.clamp(2, 0, 1) == 1


def test_clamp_with_max():
    assert utils.clamp(2, None, 5) == 2
    assert utils.clamp(2, None, 1) == 1


def test_clamp_with_min():
    assert utils.clamp(2, 0, None) == 2
    assert utils.clamp(2, 3, None) == 3


def test_clamp_with_none():
    assert utils.clamp(2, None, None) == 2


def test_slot():
    class Dummy(QObject):

        signal = pyqtSignal(int)

        def __init__(self):
            super().__init__()
            self.value = 0

    dummy = Dummy()

    @utils.slot
    def test(x: int):
        dummy.value = x

    dummy.signal.connect(test)
    dummy.signal.emit(42)
    assert dummy.value == 42


def test_slot_ignore_self():
    def test(self, name: str):
        ...

    slot_args = utils._slot_args(inspect.getfullargspec(test), test)
    assert slot_args == [str]


def test_slot_add_returntype():
    def test(self, name: str) -> str:
        ...

    slot_kwargs = utils._slot_kwargs(inspect.getfullargspec(test))
    assert slot_kwargs == {"result": str}


def test_slot_fails_without_type_annotations():
    with pytest.raises(utils.AnnotationNotFound):

        @utils.slot
        def test(x):
            ...


def test_profiler(capsys):
    with utils.profile(5):
        pass
    assert "function calls" in capsys.readouterr().out


def test_flatten():
    list_of_lists = [[1, 2], [3, 4]]
    assert utils.flatten(list_of_lists) == [1, 2, 3, 4]
