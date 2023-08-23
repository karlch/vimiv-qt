# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("modeswitch.feature")


@bdd.when(bdd.parsers.parse("I toggle {mode} mode"))
def toggle_mode(mode):
    api.modes.get_by_name(mode).toggle()
