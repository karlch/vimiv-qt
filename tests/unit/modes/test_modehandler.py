# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.modehandler."""

from vimiv.modes import modehandler


def test_enter_mode_without_active_mode(mocker, cleansetup):
    mocker.patch("vimiv.utils.objreg.get")
    modehandler.enter("image")
    assert modehandler.current() == "IMAGE"


def test_store_last_mode_on_enter_mode(mocker, cleansetup):
    mocker.patch("vimiv.utils.objreg.get")
    mocker.patch.object(modehandler, "get_active_mode",
                        return_value=modehandler.modes["image"])
    modehandler.enter("command")
    modehandler.get_active_mode.assert_called_once()
    assert modehandler.modes["command"].last_mode == "image"


def test_leave_mode(mocker, cleansetup):
    mocker.patch("vimiv.utils.objreg.get")
    mocker.patch.object(modehandler, "enter")
    modehandler.modes["command"].last_mode = "image"
    modehandler.leave("command")
    modehandler.enter.assert_called_once_with("image")
