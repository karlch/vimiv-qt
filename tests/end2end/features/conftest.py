# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""bdd-like steps for end2end testing."""

import os

import pytest_bdd as bdd

from vimiv.commands import runners
from vimiv.gui import commandline, statusbar, mainwindow
from vimiv.modes import modehandler, Modes

###############################################################################
#                                    When                                     #
###############################################################################


@bdd.when(bdd.parsers.parse("I run {command}"))
def run_command(command):
    mode = modehandler.current()
    command = runners.update_command(command, mode)
    func = commandline.get_command_func(":", command, mode)
    func()


@bdd.when(bdd.parsers.parse("I press {keys}"))
def key_press(qtbot, keys):
    mode = modehandler.current()
    qtbot.keyClicks(mode.widget, keys)


@bdd.when(bdd.parsers.parse("I enter {mode} mode"))
def enter_mode(mode):
    modehandler.enter(mode)


@bdd.when(bdd.parsers.parse("I leave {mode} mode"))
def leave_mode(mode):
    mode = Modes.get_by_name(mode)
    modehandler.leave(mode)


@bdd.when(bdd.parsers.parse("I enter command mode with {text}"))
def enter_command_with_text(text):
    modehandler.enter(Modes.COMMAND)
    commandline.instance().setText(":" + text)
    commandline.instance().textEdited.emit(":" + text)


@bdd.when(bdd.parsers.parse("I resize the window to {size}"))
def resize_main_window(size):
    width = int(size.split("x")[0])
    height = int(size.split("x")[1])
    mainwindow.instance().resize(width, height)


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
    bar = statusbar.statusbar
    assert bar["stack"].currentWidget() == bar["message"]
    assert message == bar["message"].text()


@bdd.then(bdd.parsers.parse("the {position} status should include {text}"))
def check_left_status(qtbot, position, text):
    bar = statusbar.statusbar
    assert bar["stack"].currentWidget() == bar["status"]
    assert text in bar[position].text()


@bdd.then("a message should be displayed")
def check_a_statusbar_message():
    bar = statusbar.statusbar
    assert bar["message"].text() != ""
    assert bar["stack"].currentWidget() == bar["message"]


@bdd.then("no message should be displayed")
def check_no_statusbar_message():
    bar = statusbar.statusbar
    assert bar["message"].text() == ""
    assert bar["stack"].currentWidget() == bar["status"]


@bdd.then(bdd.parsers.parse("the working directory should be {basename}"))
def check_working_directory(basename):
    assert os.path.basename(os.getcwd()) == basename


@bdd.then("the window should be fullscreen")
def check_fullscreen():
    assert mainwindow.instance().isFullScreen()


@bdd.then("the window should not be fullscreen")
def check_not_fullscreen():
    assert not mainwindow.instance().isFullScreen()


@bdd.then(bdd.parsers.parse("the mode should be {mode}"))
def check_mode(mode, qtbot):
    mode = Modes.get_by_name(mode)
    assert modehandler.current() == mode, \
        "Modehandler did not switch to %s" % (mode.name)
