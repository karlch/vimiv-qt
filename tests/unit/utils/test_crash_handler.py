# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2022 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.crash_handler."""

import collections
import functools
import signal
import sys
import types

import pytest

from vimiv.utils import crash_handler, log, customtypes


@pytest.fixture
def print_logging():
    """Fixture to reassign logging to stdout for easier capturing."""
    info, error, fatal = log.info, log.error, log.fatal
    log.info = log.error = log.fatal = functools.partial(print, end="")
    yield
    log.info, log.error, log.fatal = info, error, fatal


@pytest.fixture
def handler(mocker, print_logging):
    """Fixture to set up the crash handler with a mock app and mock excepthook."""
    initial_excepthook = sys.excepthook
    mock_excepthook = mocker.Mock()
    sys.excepthook = mock_excepthook
    app = mocker.Mock()
    instance = crash_handler.CrashHandler(app)
    yield collections.namedtuple("HandlerFixture", ["instance", "app", "excepthook"])(
        instance, app, mock_excepthook
    )
    sys.excepthook = initial_excepthook


def test_crash_handler_updates_excepthook(handler):
    assert not isinstance(sys.excepthook, types.BuiltinFunctionType)


def test_crash_handler_excepthook(capsys, handler):
    # Call system excepthook with some error
    error = ValueError("Not a number")
    sys.excepthook(type(error), error, None)
    # Check log output
    captured = capsys.readouterr()
    assert (
        captured.out == "Uncaught exception! Exiting gracefully and printing stack..."
    )
    # Check default excepthook called
    handler.excepthook.assert_called_once_with(type(error), error, None)
    # Check if graceful quit was called
    handler.app.exit.assert_called_once_with(1)


def test_crash_handler_exception_in_excepthook(capsys, handler):
    # Setup app exit to throw an exception
    def broken(_returncode):
        raise KeyError("I lost something")

    handler.app.exit = broken
    # Call system excepthook with some error checking for system exit
    error = ValueError("Not a number")
    with pytest.raises(SystemExit, match=str(customtypes.Exit.err_suicide)):
        sys.excepthook(type(error), error, None)
    # Check log output
    captured = capsys.readouterr()
    assert "I lost something" in captured.out
    assert "suicide" in captured.out


def test_crash_handler_first_interrupt(qtbot, capsys, handler):
    handler.instance.handle_interrupt(signal.SIGINT, None)
    # Check log output
    captured = capsys.readouterr()
    assert "SIGINT/SIGTERM" in captured.out

    def check_app_exit():
        exitstatus = customtypes.Exit.signal + signal.SIGINT
        handler.app.exit.assert_called_once_with(exitstatus)

    qtbot.waitUntil(check_app_exit)

    # Check if more forceful handler was installed
    assert (
        signal.getsignal(signal.SIGINT)
        == signal.getsignal(signal.SIGTERM)
        == handler.instance.handle_interrupt_forcefully
    )


def test_crash_handler_second_interrupt(capsys, handler):
    # Check if sys.exit is called with the correct return code
    with pytest.raises(SystemExit, match=str(customtypes.Exit.signal + signal.SIGINT)):
        handler.instance.handle_interrupt_forcefully(signal.SIGINT, None)
    # Check log output
    captured = capsys.readouterr()
    assert "kill signal" in captured.out
