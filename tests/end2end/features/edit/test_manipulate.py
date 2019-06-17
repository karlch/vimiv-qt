# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.imutils import immanipulate

bdd.scenarios("manipulate.feature")


@bdd.then(bdd.parsers.parse("The {name} value should be {value}"))
def manipulate_value(name, value):
    value = int(value)
    # TODO check if image itself changed
    # Find the correct manipulation
    for manipulation in immanipulate.instance().manipulations:
        if manipulation.name == name:
            assert manipulation.value == value  # Actual value
            assert manipulation.bar.value() == value  # Displayed bar
