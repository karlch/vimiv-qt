# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest
import pytest_bdd as bdd

from vimiv import api
from vimiv.gui import keyhint_widget, eventhandler


@pytest.fixture()
def keyhint():
    return api.objreg.get(keyhint_widget.KeyhintWidget)


bdd.scenarios("keyhint.feature")


@bdd.given("I re-initialize the keyhint widget")
def reinitialize_keyhint():
    api.settings.keyhint.delay.value = 5
    api.settings.keyhint.timeout.value = 100
    eventhandler.KeyHandler.partial_handler.clear_keys()


@bdd.when("I wait for the keyhint widget")
def wait_for_keyhint_widget(keyhint, qtbot):
    with qtbot.waitSignal(keyhint._show_timer.timeout, 100):
        pass


@bdd.when("I wait for the keyhint widget timeout")
def wait_for_keyhint_widget_timeout(qtbot):
    with qtbot.waitSignal(eventhandler.KeyHandler.partial_handler.partial_cleared, 500):
        pass


@bdd.then("the keyhint widget should be visible")
def keyhint_widget_visible(keyhint):
    assert keyhint.isVisible()


@bdd.then("the keyhint widget should not be visible")
def keyhint_widget_not_visible(keyhint):
    assert not keyhint.isVisible()


@bdd.then(bdd.parsers.parse("the keyhint widget should contain {command}"))
def keyhint_widget_contains(keyhint, command):
    assert command in keyhint.text()


@bdd.then("the keyhint widget should be above the statusbar")
def keyhint_widget_above_bar(keyhint, bar):
    keyhint_bottom = keyhint.y() + keyhint.height()
    bar_top = bar.y()
    assert keyhint_bottom == bar_top


@bdd.then("the keyhint widget should be at the bottom")
def keyhint_widget_bottom(keyhint, mainwindow):
    keyhint_bottom = keyhint.y() + keyhint.height()
    window_bottom = mainwindow.height()
    assert keyhint_bottom == window_bottom
