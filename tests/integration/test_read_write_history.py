# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for reading and writing history to file."""

from vimiv.commands import history


def test_create_empty_history_file(tmpdir, mocker):
    histfile = tmpdir.join("history")
    mocker.patch("vimiv.utils.xdg.join_vimiv_data", return_value=str(histfile))
    history.read()
    assert histfile.read() == ""


def test_read_existing_history_file(tmpdir, mocker):
    histfile = tmpdir.join("history")
    mocker.patch("vimiv.utils.xdg.join_vimiv_data", return_value=str(histfile))
    histfile.write(":zoom in\n:zoom out\n")
    commands = history.read()
    assert commands == [":zoom in", ":zoom out"]


def test_write_history_file(tmpdir, mocker):
    histfile = tmpdir.join("history")
    mocker.patch("vimiv.utils.xdg.join_vimiv_data", return_value=str(histfile))
    commands =  [":scroll left", ":scroll right"]
    history.write(commands)
    assert histfile.read() == ":scroll left\n:scroll right\n"
