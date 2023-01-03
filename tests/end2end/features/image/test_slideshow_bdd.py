# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2023 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api
from vimiv.imutils import slideshow


bdd.scenarios("slideshow.feature")


@pytest.fixture
def sshow():
    instance = slideshow._timer
    yield instance
    instance.stop()


@bdd.given(bdd.parsers.parse("I forcefully set the slideshow delay to {delay:d}ms"))
def set_slideshow_delay(sshow, delay):
    """Set the slideshow delay to a small value to increase test speed."""
    sshow.setInterval(delay)


@bdd.then("the slideshow should be playing")
def check_slideshow_playing(sshow):
    assert sshow.isActive()


@bdd.then("the slideshow should not be playing")
def check_slideshow_not_playing(sshow):
    assert not sshow.isActive()


@bdd.then(bdd.parsers.parse("the slideshow delay should be {delay:f}"))
def check_slideshow_delay(sshow, delay):
    # Check setting
    assert api.settings.slideshow.delay.value == delay
    # Check actual value
    assert sshow.interval() == delay * 1000


@bdd.when(bdd.parsers.parse("I let the slideshow run {repeat:d} times"))
def wait_slideshow_signal(qtbot, sshow, repeat):
    for _ in range(repeat):
        # Wait for slideshow delay and give it a small buffer
        with qtbot.waitSignal(sshow.timeout, timeout=int(sshow.interval() * 1.2)):
            pass
