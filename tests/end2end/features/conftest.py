# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Fixtures and bdd-like steps for usage during end2end testing."""

import os

from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFocusEvent
from PyQt5.QtWidgets import QApplication

import pytest
import pytest_bdd as bdd

import vimiv.gui.library
import vimiv.gui.thumbnail
import vimiv.gui.mainwindow
import vimiv.gui.message
import vimiv.gui.commandline
import vimiv.gui.bar
import vimiv.gui.image
import vimiv.gui.prompt
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


@pytest.fixture()
def image():
    yield vimiv.gui.image.ScrollableImage.instance


@pytest.fixture()
def message_widget(mainwindow):
    for overlay in mainwindow._overlays:
        if isinstance(overlay, vimiv.gui.message.Message):
            return overlay
    raise ValueError("Message widget not found")


class Counter:
    """Counter class with the count command for simple testing of commands.

    Sole purpose is to provide a command whose result, namely increasing the number, is
    easily testable without depending on other vimiv features or commands. The number is
    stored as class attribute to avoid having to deal with class instances in the object
    registry.
    """

    number = 0

    def __init__(self):
        """Reset number when a new instance is created."""
        Counter.number = 0

    @staticmethod
    @api.commands.register()
    def count(number: int = 1, count: int = 1):
        """Helper command to increase a counter used for testing."""
        Counter.number += number * count


@pytest.fixture(autouse=True)
def counter():
    """Fixture to provide a clean counter class with the count command."""
    yield Counter()


@pytest.fixture()
def answer_prompt(qtbot, mainwindow):
    """Fixture to return a function for answering the upcoming prompt.

    Uses qtbot to wait for the prompt widget and then presses the key passed to the
    function on the prompt to close it. Must be used with all prompts in one way or the
    other as they would otherwise block the running python code.
    """

    def get_prompt():
        """Retrieve the current prompt widget."""
        widgets = mainwindow.findChildren(vimiv.gui.prompt.Prompt)
        assert len(widgets) == 1, "Wrong number of prompts found"
        return widgets[0]

    def function(key):
        keys = {
            "y": Qt.Key_Y,
            "n": Qt.Key_N,
            "<return>": Qt.Key_Return,
            "<escape>": Qt.Key_Escape,
        }
        try:
            qkey = keys[key]
        except KeyError:
            raise KeyError(
                f"Unexpected prompt key '{key}', expected one of: {', '.join(keys)}"
            )

        def click_prompt_key():
            prompt = get_prompt()
            qtbot.keyClick(prompt, qkey)

        QTimer.singleShot(0, lambda: qtbot.waitUntil(click_prompt_key))

    return function


@pytest.fixture()
def keypress(qtbot):
    """Fixture to press keys on a widget handling special keys appropriately."""
    special_keys = {
        "<escape>": Qt.Key_Escape,
        "<return>": Qt.Key_Return,
        "<space>": Qt.Key_Space,
        "<backspace>": Qt.Key_Backspace,
    }

    def get_modifier(keys):
        modifiers = {
            "<ctrl>": Qt.ControlModifier,
            "<alt>": Qt.AltModifier,
            "<shift>": Qt.ShiftModifier,
        }
        for name, key in modifiers.items():
            if keys.startswith(name):
                return key, keys.replace(name, "")
        return Qt.NoModifier, keys

    def callable(widget, keys):
        modifier, keys = get_modifier(keys)
        try:
            qkey = special_keys[keys]
            qtbot.keyClick(widget, qkey, modifier=modifier)
        except KeyError:
            qtbot.keyClicks(widget, keys, modifier=modifier)

    return callable


###############################################################################
#                                    When                                     #
###############################################################################


@bdd.when(bdd.parsers.parse("I run {command}"))
def run_command(command, qtbot):
    runners.run(command, mode=api.modes.current())

    # Wait for external command to complete if any was run
    external_runner = runners.external._impl
    if external_runner is not None:

        def external_finished():
            state = external_runner.state()
            assert state == QProcess.NotRunning, "external command timed out"

        qtbot.waitUntil(external_finished, timeout=30000)


@bdd.when(bdd.parsers.parse("I press '{keys}'"))
def key_press(qtbot, keypress, keys):
    mode = api.modes.current()
    keypress(mode.widget, keys)
    # Process commandline if needed
    if keys == "<return>" and mode.name == "command":
        qtbot.wait(10)


@bdd.when(bdd.parsers.parse("I enter {mode} mode"))
def enter_mode(mode):
    api.modes.get_by_name(mode).enter()


@bdd.when(bdd.parsers.parse("I close {mode} mode"))
def leave_mode(mode):
    api.modes.get_by_name(mode).close()


@bdd.when(bdd.parsers.parse("I resize the window to {size}"))
def resize_main_window(mainwindow, size):
    width = int(size.split("x")[0])
    height = int(size.split("x")[1])
    mainwindow.resize(width, height)


@bdd.when("I wait for the working directory handler")
def wait_for_working_directory_handler(qtbot):
    with qtbot.waitSignal(api.working_directory.handler.changed):
        pass


@bdd.when(bdd.parsers.parse("I unfocus {widget_name}"))
def focus_widget(image, library, widget_name):
    names = {"the library": library, "the image": image}
    try:
        widget = names[widget_name]
    except KeyError:
        raise KeyError(
            f"Unknown widget '{widget_name}'. Currently supported: {', '.join(names)}"
        )
    event = QFocusEvent(QFocusEvent.FocusOut)
    widget.focusOutEvent(event)


@bdd.when(bdd.parsers.parse("I plan to answer the prompt with {key}"))
def run_command_answering_prompt(answer_prompt, key):
    answer_prompt(key)


@bdd.when(bdd.parsers.parse("I create the directory '{name}'"))
def create_directory(name):
    os.makedirs(name, mode=0o777)


@bdd.when(bdd.parsers.parse("I create the file '{name}'"))
def create_file(name):
    assert not os.path.exists(name), f"Not overriding existing file '{name}'"
    with open(name, "w") as f:
        f.write("")


@bdd.when(bdd.parsers.parse("I create the tag file '{name}'"))
def create_tag_file(name):
    os.makedirs(api.mark.tagdir, mode=0o700, exist_ok=True)
    path = os.path.join(api.mark.tagdir, name)
    with open(path, "w") as f:
        f.write("")


###############################################################################
#                                    Then                                     #
###############################################################################


@bdd.then("no crash should happen")
def no_crash(qtbot):
    """Don't do anything, exceptions fail the test anyway."""
    qtbot.wait(1)


@bdd.then(bdd.parsers.parse("the {position} status should include {text}"))
def check_status_text(qtbot, position, text):
    bar = statusbar.statusbar
    message = f"statusbar {position} should include {text}"

    def check_status():
        assert text in getattr(bar, position).text(), message

    qtbot.waitUntil(check_status, timeout=100)
    assert bar.isVisible()


@bdd.then(bdd.parsers.parse("the message\n'{message}'\nshould be displayed"))
def check_message(qtbot, message_widget, message):
    def check():
        assert message == message_widget.text(), "Message expected: '{message}'"

    qtbot.waitUntil(check, timeout=100)
    assert message_widget.isVisible()


@bdd.then("a message should be displayed")
def check_any_message(qtbot, message_widget):
    def check():
        assert message_widget.text(), "Any message expected"

    qtbot.waitUntil(check, timeout=100)
    assert message_widget.isVisible()


@bdd.then("no message should be displayed")
def check_no_message(qtbot, message_widget):
    def check():
        assert not message_widget.text(), "No message expected"

    qtbot.waitUntil(check, timeout=100)
    assert not message_widget.isVisible()


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
    assert api.modes.current() == mode, f"Modehandler did not switch to {mode.name}"


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


@bdd.then(bdd.parsers.parse("the thumbnail number {N:d} should be selected"))
def check_selected_thumbnail(thumbnail, qtbot, N):
    assert thumbnail.currentRow() + 1 == N


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


@bdd.then(bdd.parsers.parse("the count should be {number:d}"))
def check_count(counter, number):
    assert counter.number == number


@bdd.then(bdd.parsers.parse("the text in the command line should be {text}"))
def check_commandline_text(commandline, text):
    assert commandline.text() == text


@bdd.then(bdd.parsers.parse("the boolean setting '{name}' should be '{value}'"))
def check_boolean_setting(name, value):
    bool_value = True if value.lower() == "true" else False
    assert api.settings.get_value(name) is bool_value
