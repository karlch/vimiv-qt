# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.api.objreg."""

import pytest

from vimiv.api import objreg


class Multiplier:
    """Test class to be registered in the objreg with a simple test method."""

    instance = None

    @objreg.register
    def __init__(self, factor):
        self._factor = factor

    def multiply_by(self, number):
        return number * self._factor


@pytest.fixture()
def multiply_by_two():
    """Fixture to create a multiplier instance that multiplies by two."""
    multiplier = Multiplier(2)
    yield multiplier
    Multiplier.instance = None


def test_call_with_instance(multiply_by_two):
    number = 42
    result = objreg._call_with_instance(Multiplier.multiply_by, number)
    assert result == 2 * number


def test_call_without_instance():
    def func(argument):
        return argument * 2

    argument = 42

    assert func(argument) == objreg._call_with_instance(func, argument)
