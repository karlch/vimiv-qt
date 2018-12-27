# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.commands import aliases
from vimiv.modes import Modes


bdd.scenarios("aliases.feature")


@bdd.then(bdd.parsers.parse("the alias {name} should not exist"))
def check_alias_non_existent(name):
    assert name not in aliases.get(Modes.GLOBAL)
