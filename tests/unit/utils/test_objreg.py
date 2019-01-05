# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.objreg."""

from vimiv.utils import objreg


class DummyObject:

    """DummyObject to store in the registry."""

    @objreg.register
    def __init__(self):
        pass


def test_register_object_via_decorator():
    dummy = DummyObject()
    assert objreg.get(DummyObject) == dummy


def test_register_object_via_function():
    data = [1, 2, 3, 4, 5]
    objreg.register_object(data)
    assert objreg.get(list) == data
