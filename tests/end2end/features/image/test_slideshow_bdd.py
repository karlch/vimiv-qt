# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv.config import settings
from vimiv.utils import objreg


bdd.scenarios("slideshow.feature")


@bdd.given(bdd.parsers.parse("I forcefully set the slideshow delay to {N}ms"))
def set_slideshow_delay(N):
    """Set the slideshow delay to a small value to increase test speed."""
    slideshow = objreg.get("slideshow")
    slideshow.setInterval(int(N))


@bdd.then("the slideshow should be playing")
def check_slideshow_playing():
    slideshow = objreg.get("slideshow")
    assert slideshow.isActive()


@bdd.then("the slideshow should not be playing")
def check_slideshow_not_playing():
    slideshow = objreg.get("slideshow")
    assert not slideshow.isActive()


@bdd.then(bdd.parsers.parse("the slideshow delay should be {delay}"))
def check_slideshow_delay(delay):
    delay = float(delay)
    # Check setting
    assert settings.get_value("slideshow.delay") == delay
    # Check actual value
    slideshow = objreg.get("slideshow")
    assert slideshow.interval() == delay * 1000
