# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api
from vimiv.gui import keyhint_widget
from vimiv.utils import eventhandler


bdd.scenarios("keyhint.feature")


@bdd.given("I re-initialize the keyhint widget")
def reinitialize_keyhint():
    api.settings.KEYHINT_DELAY.value = 5
    api.settings.KEYHINT_TIMEOUT.value = 100
    eventhandler.KeyHandler.partial_handler.clear_keys()


@bdd.when("I wait for the keyhint widget")
def wait_for_keyhint_widget(qtbot):
    with qtbot.waitSignal(keyhint_widget.instance()._show_timer.timeout, 100):
        pass


@bdd.when("I wait for the keyhint widget timeout")
def wait_for_keyhint_widget_timeout(qtbot):
    with qtbot.waitSignal(eventhandler.KeyHandler.partial_handler.partial_cleared, 500):
        pass


@bdd.then("the keyhint widget should be visible")
def keyhint_widget_visible():
    assert keyhint_widget.instance().isVisible()


@bdd.then("the keyhint widget should not be visible")
def keyhint_widget_not_visible():
    assert not keyhint_widget.instance().isVisible()


@bdd.then(bdd.parsers.parse("the keyhint widget should contain {command}"))
def keyhint_widget_contains(command):
    assert command in keyhint_widget.instance().text()
