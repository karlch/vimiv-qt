# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for the interaction between the commandline and the statusbar."""

import pytest

from vimiv.commands import commands, cmdexc, runners
from vimiv.gui import statusbar

@pytest.fixture
def sb(qtbot, mocker, cleansetup):
    """Set up statusbar widget and patch used methods."""
    sbar = statusbar.StatusBar()
    qtbot.addWidget(sbar)
    mocker.patch.object(sbar, "message")
    mocker.patch.object(sbar, "update")
    yield sbar


def test_command_updates_statusbar(sb, qtbot):
    @commands.register()
    def simple():
        pass
    # Wait for QTimer
    with qtbot.waitSignal(runners.signals.exited, timeout=100):
        runners.CommandRunner()("simple", "image")
    sb.update.assert_called_once()


def test_unkown_command_shows_error_message(sb):
    runners.CommandRunner()("not_a_cmd", "image")
    sb.message.assert_called_once_with(
        "not_a_cmd: unknown command for mode image", "Error")


def test_unknown_command_in_other_mode_shows_error_message(sb):
    @commands.register(mode="image")
    def image():
        pass
    runners.CommandRunner()("image", "library")
    sb.message.assert_called_once_with(
        "image: unknown command for mode library", "Error")


def test_command_with_error_shows_error_message(sb):
    @commands.register()
    def error():
        raise cmdexc.CommandError("Broken")
    runners.CommandRunner()("error", "image")
    sb.message.assert_called_once_with("error: Broken", "Error")


def test_command_with_wrong_arg_shows_error_message(sb):
    @commands.register()
    def error():
        pass
    runners.CommandRunner()("error --arg", "image")
    sb.message.assert_called_once_with(
        "error: Unrecognized arguments: --arg", "Error")
