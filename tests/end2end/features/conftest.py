# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""bdd-like steps for end2end testing."""

import os

import pytest_bdd as bdd

from vimiv.commands import cmdrunner
from vimiv.modes import modehandler
from vimiv.utils import objreg

###############################################################################
#                                    When                                     #
###############################################################################


@bdd.when(bdd.parsers.parse("I run {command}"))
def run_command(command):
    cmdrunner.run(command)


@bdd.when(bdd.parsers.parse("I press {keys}"))
def key_press(qtbot, keys):
    mode = modehandler.current()
    widget = objreg.get(mode)
    qtbot.keyClicks(widget, keys)


@bdd.when(bdd.parsers.parse("I enter {mode} mode"))
def enter_mode(mode):
    modehandler.enter(mode)


@bdd.when(bdd.parsers.parse("I leave {mode} mode"))
def leave_mode(mode):
    modehandler.leave(mode)


@bdd.when(bdd.parsers.parse("I enter command mode with {text}"))
def enter_command_with_text(vimivproc, text):
    modehandler.enter("command")
    cmd = objreg.get("command")
    cmd .setText(":" + text)
    cmd.textEdited.emit(":" + text)


@bdd.when(bdd.parsers.parse("I resize the window to {size}"))
def resize_main_window(size):
    width = int(size.split("x")[0])
    height = int(size.split("x")[1])
    mw = objreg.get("mainwindow")
    mw.resize(width, height)


@bdd.when(bdd.parsers.parse("I wait for {N}ms"))
def wait(qtbot, N):
    qtbot.wait(int(N))


###############################################################################
#                                    Then                                     #
###############################################################################


@bdd.then("no crash should happen")
def no_crash(qtbot):
    """Don't do anything, exceptions fail the test anyway."""
    qtbot.wait(0.01)


@bdd.then(bdd.parsers.parse("the message\n'{message}'\nshould be displayed"))
def check_statusbar_message(message):
    bar = objreg.get("statusbar")
    assert bar["stack"].currentWidget() == bar["message"]
    assert message == bar["message"].text()


@bdd.then(bdd.parsers.parse("the {position} status should include {text}"))
def check_left_status(qtbot, position, text):
    bar = objreg.get("statusbar")
    assert bar["stack"].currentWidget() == bar["status"]
    assert text in bar[position].text()


@bdd.then("a message should be displayed")
def check_a_statusbar_message():
    bar = objreg.get("statusbar")
    assert bar["message"].text() != ""
    assert bar["stack"].currentWidget() == bar["message"]


@bdd.then("no message should be displayed")
def check_no_statusbar_message():
    bar = objreg.get("statusbar")
    assert bar["message"].text() == ""
    assert bar["stack"].currentWidget() == bar["status"]


@bdd.then(bdd.parsers.parse("the working directory should be {basename}"))
def check_working_directory(basename):
    assert os.path.basename(os.getcwd()) == basename
