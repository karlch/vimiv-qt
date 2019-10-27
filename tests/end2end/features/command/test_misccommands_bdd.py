# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import time

import pytest_bdd as bdd


bdd.scenarios("misccommands.feature")


@bdd.given("I start a timer")
def starttime():
    yield time.time()


@bdd.then(bdd.parsers.parse("at least {duration:f} seconds should have elapsed"))
def check_time_elapsed(starttime, duration):
    elapsed = time.time() - starttime
    assert elapsed >= duration
    starttime = None
