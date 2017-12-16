# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

from vimiv.gui import mainwindow


def test_toggle_fullscreen(mocker, qtbot, objregistry):
    mocker.patch.object(mainwindow.MainWindow, "init_bar")
    mocker.patch.object(mainwindow.MainWindow, "init_image")
    mw = mainwindow.MainWindow()
    qtbot.addWidget(mw)
    mw.fullscreen()
    assert mw.isFullScreen() is True
    mw.fullscreen()
    assert mw.isFullScreen() is False
