# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.gui.statusbar."""

from vimiv.gui import statusbar


def test_statusbar_module():
    @statusbar.module("{simple}")
    def simple_module():
        return "text"
    assert statusbar.evaluate_modules("{simple}") == "text"


def test_update_statusbar(mocker, qtbot):
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch("vimiv.config.settings.get_value", return_value="text")
    sb.update()
    assert sb["left"].text() == "text"
    assert sb["center"].text() == "text"
    assert sb["right"].text() == "text"


def test_update_statusbar_from_module(mocker, qtbot):
    sb = statusbar.StatusBar()
    qtbot.addWidget(sb)
    mocker.patch.object(sb, "update")
    statusbar.update()
    sb.update.assert_called_once()
