# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv import api
from vimiv.commands import aliases


bdd.scenarios("aliases.feature")


@bdd.then(bdd.parsers.parse("the alias {name} should not exist"))
def check_alias_non_existent(name):
    assert name not in aliases.get(api.modes.GLOBAL)
