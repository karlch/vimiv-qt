# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api
from vimiv.imutils import slideshow


bdd.scenarios("slideshow.feature")


@pytest.fixture
def sshow():
    return slideshow.instance()


@bdd.given(bdd.parsers.parse("I forcefully set the slideshow delay to {N}ms"))
def set_slideshow_delay(sshow, N):
    """Set the slideshow delay to a small value to increase test speed."""
    sshow.setInterval(int(N))


@bdd.then("the slideshow should be playing")
def check_slideshow_playing(sshow):
    assert sshow.isActive()


@bdd.then("the slideshow should not be playing")
def check_slideshow_not_playing(sshow):
    assert not sshow.isActive()


@bdd.then(bdd.parsers.parse("the slideshow delay should be {delay}"))
def check_slideshow_delay(sshow, delay):
    delay = float(delay)
    # Check setting
    assert api.settings.slideshow.delay.value == delay
    # Check actual value
    assert sshow.interval() == delay * 1000


@bdd.when(bdd.parsers.parse("I let the slideshow run {N:d} times"))
def wait_slideshow_signal(qtbot, sshow, N):
    for i in range(N):
        # Wait for slideshow delay and give it a small buffer
        with qtbot.waitSignal(sshow.timeout, timeout=int(sshow.interval() * 1.2)):
            pass
