# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

import pytest_bdd as bdd

from vimiv import api
from vimiv.utils import log


bdd.scenarios("message.feature")


@bdd.when(bdd.parsers.parse("I log the warning '{message}'"))
def log_warning(message, qtbot):
    log.warning(message)


@bdd.when("I clear the status")
def clear_status():
    api.status.clear("clear in bdd step")


@bdd.then("the bar should be visible")
def check_bar_visible(bar):
    assert bar.isVisible()


@bdd.then("the bar should not be visible")
def check_bar_not_visible(bar):
    assert not bar.isVisible()
