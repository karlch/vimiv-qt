# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.gui.statusbar."""

import pytest

from vimiv.gui import statusbar


def test_statusbar_module():
    @statusbar.module("{simple}")
    def simple_module():
        return "text"
    assert statusbar.evaluate_modules("{simple}") == "text"


@pytest.fixture
def sb(qtbot):
    """Set up statusbar widget in qtbot."""
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    yield sb


@pytest.mark.usefixtures("cleansetup")
class TestStatusbar():

    def test_update_statusbar(self, mocker, sb):
        mocker.patch("vimiv.config.settings.get_value", return_value="text")
        sb.update()
        assert sb["left"].text() == "text"
        assert sb["center"].text() == "text"
        assert sb["right"].text() == "text"


    def test_update_statusbar_from_module(self, mocker, sb):
        mocker.patch.object(sb, "update")
        statusbar.update()
        sb.update.assert_called_once()
