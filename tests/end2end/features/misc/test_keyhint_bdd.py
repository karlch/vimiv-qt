# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytestqt
import pytest_bdd as bdd

from vimiv import api
from vimiv.gui import keyhintwidget, eventhandler


@pytest.fixture()
def keyhint(overlay):
    return overlay(keyhintwidget.KeyhintWidget)


bdd.scenarios("keyhint.feature")


@pytest.fixture(autouse=True)
def update_keyhint():
    """Fixture to shorten and reset keyhint delays."""
    delay = api.settings.keyhint.delay.value
    timeout = api.settings.keyhint.timeout.value
    api.settings.keyhint.delay.value = 1
    api.settings.keyhint.timeout.value = 10
    yield
    api.settings.keyhint.delay.value = delay
    api.settings.keyhint.timeout.value = timeout
    eventhandler.EventHandlerMixin.partial_handler.clear_keys()


@bdd.when("I wait for the keyhint widget")
def wait_for_keyhint_widget(keyhint, qtbot):
    with qtbot.waitSignal(keyhint._show_timer.timeout, timeout=100):
        pass


@bdd.when("I wait for the keyhint widget timeout")
def wait_for_keyhint_widget_timeout(qtbot):
    with qtbot.waitSignal(
        eventhandler.EventHandlerMixin.partial_handler.partial_cleared, timeout=500
    ):
        pass


@bdd.then("the keyhint widget should be visible")
def keyhint_widget_visible(keyhint):
    assert keyhint.isVisible()


@bdd.then("the keyhint widget should not be visible")
def keyhint_widget_not_visible(keyhint):
    assert not keyhint.isVisible()


@bdd.then("the keyhint widget should not appear")
def keyhint_widget_not_appeared(keyhint, qtbot):
    # Required in addition to should not be visible as the timeout does not happen and
    # waiting for the widget would raise TimeoutError
    with pytest.raises(pytestqt.exceptions.TimeoutError):
        timeout = 2 * api.settings.keyhint.delay.value
        with qtbot.waitSignal(keyhint._show_timer.timeout, timeout=timeout):
            pass


@bdd.then(bdd.parsers.parse("the keyhint widget should contain {command}"))
def keyhint_widget_contains(keyhint, command):
    assert command in keyhint.text()


@bdd.then("the keyhint widget should be above the statusbar")
def keyhint_widget_above_bar(keyhint, statusbar):
    keyhint_bottom = keyhint.y() + keyhint.height()
    bar_top = statusbar.y()
    assert keyhint_bottom == bar_top


@bdd.then("the keyhint widget should be at the bottom")
def keyhint_widget_bottom(keyhint, mainwindow):
    keyhint_bottom = keyhint.y() + keyhint.height()
    window_bottom = mainwindow.height()
    assert keyhint_bottom == window_bottom
