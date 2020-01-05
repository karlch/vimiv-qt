# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api.objreg."""

from vimiv.api import objreg


class DummyObject:

    """DummyObject to store in the registry."""

    @objreg.register
    def __init__(self):
        pass


def test_register_object_via_decorator():
    dummy = DummyObject()
    assert DummyObject.instance == dummy
