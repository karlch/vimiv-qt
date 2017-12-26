# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

import pytest

from vimiv.gui import mainwindow


@pytest.fixture
def main_win(mocker, qtbot):
    """Set up clean mainwindow."""
    mocker.patch("vimiv.gui.image")
    mocker.patch("vimiv.gui.library")
    mocker.patch("vimiv.config.styles.get", return_value="#000000")
    mocker.patch("vimiv.gui.bar")
    mocker.patch("vimiv.gui.completionwidget")
    mocker.patch("vimiv.gui.statusbar.update")
    mw = mainwindow.MainWindow()
    qtbot.addWidget(mw)
    yield mw


@pytest.mark.usefixtures("cleansetup")
class TestMainWindow():

    def test_toggle_fullscreen(self, main_win):
        main_win.fullscreen()
        assert main_win.isFullScreen() is True
        main_win.fullscreen()
        assert main_win.isFullScreen() is False
