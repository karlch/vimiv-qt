# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""bdd-like steps for end2end testing."""

import os

from PyQt5.QtCore import Qt

import pytest_bdd as bdd

from vimiv import api, apimodules
from vimiv.commands import runners
from vimiv.gui import commandline, statusbar, mainwindow, library, thumbnail
from vimiv.imutils import imstorage

###############################################################################
#                                    When                                     #
###############################################################################


@bdd.when(bdd.parsers.parse("I run {command}"))
def run_command(command):
    mode = api.modes.current()
    command = runners.update_command(command, mode)
    func = commandline._command_func(":", command, mode)
    func()


@bdd.when(bdd.parsers.parse("I press {keys}"))
def key_press(qtbot, keys):
    mode = api.modes.current()
    qtbot.keyClicks(mode.widget, keys)


@bdd.when("I activate the command line")
def activate_commandline(qtbot):
    """Needed as passing return as a string is not possible."""
    qtbot.keyClick(commandline.instance(), Qt.Key_Return)
    qtbot.wait(10)


@bdd.when(bdd.parsers.parse("I enter {mode} mode"))
def enter_mode(mode):
    apimodules.enter(mode)


@bdd.when(bdd.parsers.parse("I leave {mode} mode"))
def leave_mode(mode):
    api.modes.leave(api.modes.get_by_name(mode))


@bdd.when(bdd.parsers.parse("I enter command mode with {text}"))
def enter_command_with_text(text):
    api.modes.enter(api.modes.COMMAND)
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
    mode = api.modes.get_by_name(mode)
    assert api.modes.current() == mode, "Modehandler did not switch to %s" % (mode.name)


@bdd.then(bdd.parsers.parse("the library row should be {row}"))
def check_row_number(row):
    assert library.instance().row() + 1 == int(row)


@bdd.then(bdd.parsers.parse("the image should have the index {index}"))
def check_image_index(index):
    assert imstorage.get_index() == index


@bdd.given("I enter thumbnail mode")
def enter_thumbnail():
    api.modes.enter(api.modes.THUMBNAIL)
    thumbnail.instance().setFixedWidth(400)  # Make sure width is as expected


@bdd.then(bdd.parsers.parse("the thumbnail number {N} should be selected"))
def check_selected_thumbnail(qtbot, N):
    thumb = thumbnail.instance()
    assert thumb.currentRow() + 1 == int(N)
