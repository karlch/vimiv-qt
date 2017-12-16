# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.gui.commandline."""

from vimiv.commands import commands, external
from vimiv.gui import commandline


def test_run_internal_command(qtbot, mocker):
    mocker.patch.object(commands, "run")
    cmdline = commandline.CommandLine()
    qtbot.addWidget(cmdline)
    cmdline.setText(":zoom in")
    cmdline.returnPressed.emit()
    commands.run.assert_called_once_with("zoom in")


def test_run_external_command(qtbot, mocker):
    mocker.patch.object(external, "run")
    cmdline = commandline.CommandLine()
    qtbot.addWidget(cmdline)
    cmdline.setText(":!ls")
    cmdline.returnPressed.emit()
    external.run.assert_called_once_with("ls")
