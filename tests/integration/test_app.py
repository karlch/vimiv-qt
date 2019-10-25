# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Integration tests for vimiv.app.

These are not unit tests as the app makes use of multiple modules."""

import time

import pytest

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication

import vimiv.app
from vimiv.utils import asyncrun


@pytest.fixture()
def app(mocker):
    mocker.patch.object(QApplication, "exit")  # Do not want to quit the global app
    instance = vimiv.app.Application()
    QThreadPool.globalInstance().waitForDone()  # Ensure parallel tasks are done
    yield instance
    instance.quit()
    QApplication.exit.assert_called_with(0)


@pytest.mark.ci_skip
def test_load_icon(app):
    assert not app.windowIcon().isNull()


def test_wait_for_running_processes(mocker, app):
    def process():
        time.sleep(0.001)
        callback()

    callback = mocker.Mock()
    asyncrun(process)
    app.quit()
    callback.assert_called_once()
