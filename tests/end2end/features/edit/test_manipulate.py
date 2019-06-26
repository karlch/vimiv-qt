# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.imutils import immanipulate

bdd.scenarios("manipulate.feature")


@bdd.when("I apply any manipulation")
def wait_for_beer(qtbot):
    manipulator = immanipulate.instance()
    with qtbot.waitSignal(immanipulate.instance().updated) as _:
        manipulator.set(10)


@bdd.then(bdd.parsers.parse("The current value should be {value:d}"))
def check_current_manipulation_value(value):
    manipulation = immanipulate.instance()._current
    assert manipulation.value == value  # Actual value


@bdd.then(bdd.parsers.parse("The current manipulation should be {name}"))
def check_current_manipulation_name(name):
    manipulation = immanipulate.instance()._current
    assert manipulation.name == name


@bdd.then(bdd.parsers.parse("There should be {n_changes:d} stored changes"))
def check_stored_changes(n_changes):
    assert len(immanipulate.instance()._changes) == n_changes
