# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.gui.commandline."""

import pytest

from vimiv.commands import commands, external
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
        mocker.patch.object(commands, "run")
        cmdline.setText(":zoom in")
        cmdline.returnPressed.emit()
        commands.run.assert_called_once_with("zoom in")


    def test_run_external_command(self, mocker, cmdline):
        mocker.patch.object(external, "run")
        cmdline.setText(":!ls")
        cmdline.returnPressed.emit()
        external.run.assert_called_once_with("ls")
