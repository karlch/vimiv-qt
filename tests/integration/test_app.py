# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Integration tests for vimiv.app.

These are not unit tests as the app makes use of multiple modules."""

import time

import pytest

import vimiv.app
from vimiv.utils import asyncrun


@pytest.mark.ci_skip
def test_load_icon(qtbot):
    icon = vimiv.app.Application.get_icon()
    assert not icon.isNull()


def test_wait_for_running_processes(mocker):
    """Ensure any running threads are completed before the app exits."""

    def process():
        time.sleep(0.001)
        callback()

    callback = mocker.Mock()
    asyncrun(process)
    vimiv.app.Application.preexit(0)
    callback.assert_called_once()
