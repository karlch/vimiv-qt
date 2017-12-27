# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.
"""Tests for vimiv.gui.commandline."""

import pytest

from vimiv.gui import commandline


@pytest.fixture
def cmdline(mocker, qtbot):
    """Set up commandline widget in qtbot."""
    mocker.patch("vimiv.utils.objreg.get")  # Do not try to get completion
    my_cmdline = commandline.CommandLine()
    qtbot.addWidget(my_cmdline)
    yield my_cmdline


@pytest.mark.usefixtures("cleansetup")
class TestCommandline():

    def test_run_internal_command(self, mocker, cmdline, qtbot):
        mocker.patch.object(cmdline, "runners")
        mocker.patch("vimiv.modes.modehandler.last", return_value="image")
        cmdline.setText(":zoom in")
        cmdline.returnPressed.emit()
        def runner_called():
            cmdline.runners["command"].assert_called_once_with("zoom in", "image")
        qtbot.waitUntil(runner_called, timeout=100)


    def test_run_external_command(self, mocker, cmdline, qtbot):
        mocker.patch.object(cmdline, "runners")
        cmdline.setText(":!ls")
        cmdline.returnPressed.emit()
        def runner_called():
            cmdline.runners["external"].assert_called_once_with("ls")
        qtbot.waitUntil(runner_called, timeout=100)
