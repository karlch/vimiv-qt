# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Functions, fixtures and bdd-like steps for end2end testing."""

import os

from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QApplication

import pytest
import pytest_bdd as bdd

import vimiv.gui.library
import vimiv.gui.thumbnail
import vimiv.gui.mainwindow
import vimiv.gui.commandline
import vimiv.gui.bar
from vimiv import api
from vimiv.commands import runners
from vimiv.gui import statusbar
from vimiv.imutils import filelist


########################################################################################
#                                   Pytest fixtures                                    #
########################################################################################
@pytest.fixture()
def library():
    yield vimiv.gui.library.Library.instance


@pytest.fixture()
def thumbnail():
    yield vimiv.gui.thumbnail.ThumbnailView.instance


@pytest.fixture()
def mainwindow():
    yield vimiv.gui.mainwindow.MainWindow.instance


@pytest.fixture()
def commandline():
    yield vimiv.gui.commandline.CommandLine.instance


@pytest.fixture()
def bar():
    yield vimiv.gui.bar.Bar.instance


###############################################################################
#                                    When                                     #
###############################################################################


@bdd.when(bdd.parsers.parse("I run {command}"))
def run_command(command):
    runners.run(command, mode=api.modes.current())


@bdd.when(bdd.parsers.parse("I press {keys}"))
def key_press(qtbot, keys):
    mode = api.modes.current()
    qtbot.keyClicks(mode.widget, keys)


@bdd.when("I activate the command line")
def activate_commandline(commandline, qtbot):
    """Needed as passing return as a string is not possible."""
    qtbot.keyClick(commandline, Qt.Key_Return)
    qtbot.wait(10)


@bdd.when(bdd.parsers.parse("I enter {mode} mode"))
def enter_mode(mode):
    api.modes.get_by_name(mode).enter()


@bdd.when(bdd.parsers.parse("I leave {mode} mode"))
def leave_mode(mode):
    api.modes.get_by_name(mode).leave()


@bdd.when(bdd.parsers.parse('I enter command mode with "{text}"'))
def enter_command_with_text(commandline, text):
    api.modes.COMMAND.enter()
    commandline.setText(":" + text)
    commandline.textEdited.emit(":" + text)


@bdd.when(bdd.parsers.parse("I resize the window to {size}"))
def resize_main_window(mainwindow, size):
    width = int(size.split("x")[0])
    height = int(size.split("x")[1])
    mainwindow.resize(width, height)


@bdd.when(bdd.parsers.parse("I wait for {N}ms"))
def wait(qtbot, N):
    qtbot.wait(int(N))


@bdd.when("I wait for the command to complete")
def wait_for_external_command(qtbot):
    """Wait until the external process has completed."""
    max_iterations = 100
    iteration = 0
    while (
        QThreadPool.globalInstance().activeThreadCount() and iteration < max_iterations
    ):
        qtbot.wait(10)
        iteration += 1
    assert iteration != max_iterations, "external command timed out"


@bdd.when("I wait for the working directory handler")
def wait_for_working_directory_handler(qtbot):
    with qtbot.waitSignal(api.working_directory.handler.changed):
        pass


###############################################################################
#                                    Then                                     #
###############################################################################


@bdd.then("no crash should happen")
def no_crash(qtbot):
    """Don't do anything, exceptions fail the test anyway."""
    qtbot.wait(1)


@bdd.then(bdd.parsers.parse("the message\n'{message}'\nshould be displayed"))
def check_statusbar_message(qtbot, message):
    bar = statusbar.statusbar
    _check_status(
        qtbot,
        lambda: message == bar.message.text(),
        info=f"Message expected: '{message}'",
    )
    assert bar.stack.currentWidget() == bar.message


@bdd.then(bdd.parsers.parse("the {position} status should include {text}"))
def check_left_status(qtbot, position, text):
    bar = statusbar.statusbar
    _check_status(
        qtbot,
        lambda: text in getattr(bar.status, position).text(),
        info=f"position {position} should include {text}",
    )
    assert bar.stack.currentWidget() == bar.status


@bdd.then("a message should be displayed")
def check_a_statusbar_message(qtbot):
    bar = statusbar.statusbar
    _check_status(qtbot, lambda: bar.message.text() != "", info="Any message expected")
    assert bar.stack.currentWidget() == bar.message


@bdd.then("no message should be displayed")
def check_no_statusbar_message(qtbot):
    bar = statusbar.statusbar
    _check_status(qtbot, lambda: bar.message.text() == "", info="No message expected")
    assert bar.stack.currentWidget() == bar.status


@bdd.then(bdd.parsers.parse("the working directory should be {basename}"))
def check_working_directory(basename):
    assert os.path.basename(os.getcwd()) == basename


@bdd.then("the window should be fullscreen")
def check_fullscreen(mainwindow):
    assert mainwindow.isFullScreen()


@bdd.then("the window should not be fullscreen")
def check_not_fullscreen(mainwindow):
    assert not mainwindow.isFullScreen()


@bdd.then(bdd.parsers.parse("the mode should be {mode}"))
def check_mode(mode, qtbot):
    mode = api.modes.get_by_name(mode)
    assert api.modes.current() == mode, "Modehandler did not switch to %s" % (mode.name)


@bdd.then(bdd.parsers.parse("the library row should be {row}"))
def check_row_number(library, row):
    assert library.row() + 1 == int(row)


@bdd.then(bdd.parsers.parse("the image should have the index {index}"))
def check_image_index(index):
    assert filelist.get_index() == index


@bdd.given("I enter thumbnail mode")
def enter_thumbnail(thumbnail):
    api.modes.THUMBNAIL.enter()
    thumbnail.setFixedWidth(400)  # Make sure width is as expected


@bdd.then(bdd.parsers.parse("the thumbnail number {N} should be selected"))
def check_selected_thumbnail(thumbnail, qtbot, N):
    assert thumbnail.currentRow() + 1 == int(N)


@bdd.then(bdd.parsers.parse("the pop up '{title}' should be displayed"))
def check_popup_displayed(title):
    for window in QApplication.topLevelWindows():
        if window.title() == title:
            window.close()
            return
    raise AssertionError(f"Window '{title}' not found")


@bdd.then(bdd.parsers.parse("the filelist should contain {number} images"))
def check_filelist_length(number):
    assert filelist.total() == number


@bdd.then(bdd.parsers.parse("the file {name} should exist"))
@bdd.then("the file <name> should exist")
def check_file_exists(name):
    assert os.path.isfile(name)


@bdd.then(bdd.parsers.parse("the file {name} should not exist"))
def check_not_file_exists(name):
    assert not os.path.isfile(name)


@bdd.then(bdd.parsers.parse("the directory {name} should exist"))
def check_directory_exists(name):
    assert os.path.isdir(name)


@bdd.then(bdd.parsers.parse("the directory {name} should not exist"))
def check_not_directory_exists(name):
    assert not os.path.isdir(name)


def _check_status(qtbot, assertion, info=""):
    """Check statusbar repeatedly as this is threaded and may take a while."""
    iteration = 0
    max_iterations = 100
    while not assertion() and iteration < max_iterations:
        qtbot.wait(10)
        iteration += 1
    assert iteration != max_iterations, "Statusbar check timed out\n" + info
