# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2021 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

import vimiv.imutils.immanipulate

bdd.scenarios("manipulate.feature", "manipulate_segfault.feature")


@pytest.fixture()
def manipulator():
    return vimiv.imutils.immanipulate.Manipulator.instance


@pytest.fixture()
def manipulation(manipulator):
    return manipulator._current_manipulation


@bdd.when("I apply any manipulation")
def apply_any_manipulation(manipulator, qtbot):
    with qtbot.waitSignal(manipulator.updated) as _:
        manipulator.goto(10)


@bdd.then(bdd.parsers.parse("The current value should be {value:d}"))
def check_current_manipulation_value(manipulation, value):
    assert manipulation.value == value  # Actual value


@bdd.then(bdd.parsers.parse("The current manipulation should be {name}"))
def check_current_manipulation_name(manipulation, name):
    assert manipulation.name == name


@bdd.then(bdd.parsers.parse("There should be {n_changes:d} stored changes"))
def check_stored_changes(manipulator, n_changes):
    assert len(manipulator._changes) == n_changes
