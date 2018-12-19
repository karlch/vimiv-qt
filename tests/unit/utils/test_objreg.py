# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.objreg."""

import pytest

from vimiv.utils import objreg


class DummyObject:

    """DummyObject to store in the registry."""

    @objreg.register("dummy")
    def __init__(self):
        pass


@pytest.fixture
def setup():
    yield
    objreg.clear()


def test_register_object_via_decorator(setup):
    dummy = DummyObject()
    assert objreg.get("dummy") == dummy


def test_register_object_via_function(setup):
    data = [1, 2, 3, 4, 5]
    objreg.register_object("data", data)
    assert objreg.get("data") == data


def test_persistent_object(setup):
    data = [1, 2, 3, 4, 5]
    objreg.register_object("data", data, True)
    objreg.clear()  # Clear does not remove the persistent object
    assert objreg.get("data") == data
    del objreg._registry["data"]


def test_raise_assertion_error_on_wrong_object(setup):
    with pytest.raises(AssertionError, match="must be of type"):
        objreg._registry["anything"] = 42
