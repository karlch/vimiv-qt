# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

from PyQt5.QtCore import Qt

import pytest_bdd as bdd

from vimiv import api


bdd.scenarios("commandline.feature")


@bdd.when("I hit backspace")
def hit_backspace(commandline, qtbot):
    """Needed as passing backspace as a string is not possible."""
    qtbot.keyClick(commandline, Qt.Key_Backspace)
    qtbot.wait(10)


@bdd.then(bdd.parsers.parse("the text in the command line should be {text}"))
def check_commandline_text(commandline, text):
    assert commandline.text() == text


@bdd.then("the mode should not be command")
def check_commandline_closed():
    assert api.modes.current() != api.modes.COMMAND
