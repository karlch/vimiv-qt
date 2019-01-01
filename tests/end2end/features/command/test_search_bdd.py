# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.commands import search
from vimiv.modes import modehandler


bdd.scenarios("search.feature")


@bdd.when(bdd.parsers.parse("I search for {text}"))
def run_search(text):
    search.search(text, modehandler.current())


@bdd.when(bdd.parsers.parse("I search in reverse for {text}"))
def run_search_reverse(text):
    search.search(text, modehandler.current(), reverse=True)
