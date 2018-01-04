# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

from PyQt5.QtCore import Qt

import pytest_bdd as bdd

from vimiv.modes import modehandler
from vimiv.utils import objreg


bdd.scenarios("commandline.feature")


@bdd.when("I activate the command line")
def activate_commandline(qtbot):
    """Needed as passing return as a string is not possible."""
    cmd = objreg.get("command")
    qtbot.keyClick(cmd, Qt.Key_Return)
    qtbot.wait(10)


@bdd.when("I hit backspace")
def hit_backspace(qtbot):
    """Needed as passing backspace as a string is not possible."""
    cmd = objreg.get("command")
    qtbot.keyClick(cmd, Qt.Key_Backspace)
    qtbot.wait(10)


@bdd.then(bdd.parsers.parse("the text in the command line should be {text}"))
def check_commandline_text(text):
    cmd = objreg.get("command")
    assert cmd.text() == text


@bdd.then("the mode should not be command")
def check_commandline_closed():
    assert modehandler.current() != "command"
