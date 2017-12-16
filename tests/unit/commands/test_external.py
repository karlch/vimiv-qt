# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.commands.external."""

from unittest.mock import Mock

from vimiv.commands import external, commands


def test_run_external_command(mocker):
    mockobj = Mock()
    commands.signals.exited.connect(mockobj)
    external.run(":")
    mockobj.assert_called_once_with(0, "")


def test_command_not_found_error():
    mockobj = Mock()
    commands.signals.exited.connect(mockobj)
    external.run("foo_bar_baz")
    mockobj.assert_called_once_with(
        127, "/bin/sh: foo_bar_baz: command not found")


def test_command_fails():
    mockobj = Mock()
    commands.signals.exited.connect(mockobj)
    external.run("ls --unknown-argument")
    mockobj.assert_called_once_with(
        2, "ls: unrecognized option '--unknown-argument'")
