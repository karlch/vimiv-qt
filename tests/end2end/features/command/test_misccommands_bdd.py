# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import time

import pytest_bdd as bdd


bdd.scenarios("misccommands.feature")


@bdd.given("I start a timer", target_fixture="starttime")
def starttime():
    return time.time()


@bdd.then(bdd.parsers.parse("at least {duration:f} seconds should have elapsed"))
def check_time_elapsed(starttime, duration):
    elapsed = time.time() - starttime
    assert elapsed >= duration
    starttime = None
