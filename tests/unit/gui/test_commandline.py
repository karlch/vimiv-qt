# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.gui.commandline."""

import pytest

from vimiv.gui import commandline


@pytest.fixture
def cmdline(qtbot):
    """Set up commandline widget in qtbot."""
    my_cmdline = commandline.CommandLine()
    qtbot.addWidget(my_cmdline)
    yield my_cmdline


@pytest.mark.usefixtures("cleansetup")
class TestCommandline():

    def test_run_internal_command(self, mocker, cmdline):
        mocker.patch.object(cmdline, "runners")
        mocker.patch("vimiv.modes.modehandler.last", return_value="image")
        cmdline.setText(":zoom in")
        cmdline.returnPressed.emit()
        cmdline.runners["command"].assert_called_once_with("zoom in", "image")


    def test_run_external_command(self, mocker, cmdline):
        mocker.patch.object(cmdline, "runners")
        cmdline.setText(":!ls")
        cmdline.returnPressed.emit()
        cmdline.runners["external"].assert_called_once_with("ls")
