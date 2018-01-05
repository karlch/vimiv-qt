# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""bdd steps for thumbnail tests."""

import pytest_bdd as bdd

from vimiv.modes import modehandler
from vimiv.utils import objreg


@bdd.given("I enter thumbnail mode")
def enter_thumbnail():
    modehandler.enter("thumbnail")


@bdd.then(bdd.parsers.parse("the thumbnail number {N} should be selected"))
def check_selected_thumbnail(N):
    thumb = objreg.get("thumbnail")
    assert thumb.columns() == 2, "Default settings not respected"
    assert thumb.currentRow() + 1 == int(N)
