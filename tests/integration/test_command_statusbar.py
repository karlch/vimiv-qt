# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for the interaction between the commandline and the statusbar."""

from vimiv.commands import commands, cmdexc
from vimiv.gui import statusbar


def test_command_updates_statusbar(mocker, qtbot, cleansetup):
    @commands.register()
    def simple():
        pass
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch.object(sb, "update")
    commands.run("simple")
    sb.update.assert_called_once()


def test_unkown_command_shows_error_message(mocker, qtbot, cleansetup):
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch.object(sb, "message")
    commands.run("not_a_cmd")
    sb.message.assert_called_once_with(
        "not_a_cmd: unknown command for mode global", "Error")


def test_unknown_command_in_other_mode_shows_error_message(
        mocker, qtbot, cleansetup):
    @commands.register(mode="image")
    def image():
        pass
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch.object(sb, "message")
    commands.run("image", "library")
    sb.message.assert_called_once_with(
        "image: unknown command for mode library", "Error")


def test_command_with_error_shows_error_message(mocker, qtbot, cleansetup):
    @commands.register()
    def error():
        raise cmdexc.CommandError("Broken")
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch.object(sb, "message")
    commands.run("error")
    sb.message.assert_called_once_with("error: Broken", "Error")


def test_command_with_wrong_arg_shows_error_message(mocker, qtbot,
                                                    cleansetup):
    @commands.register()
    def error():
        pass
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch.object(sb, "message")
    commands.run("error --arg")
    sb.message.assert_called_once_with(
        "error: Unrecognized arguments: --arg", "Error")
