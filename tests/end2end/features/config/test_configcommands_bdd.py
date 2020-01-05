# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("configcommands.feature")


@bdd.then(bdd.parsers.parse("the boolean setting '{name}' should be '{value}'"))
def check_boolean_setting(name, value):
    bool_value = True if value.lower() == "true" else False
    assert api.settings.get_value(name) is bool_value
