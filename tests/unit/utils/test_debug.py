# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.debug"""

import time

import pytest

from vimiv.utils import debug, log


def test_profiler(capsys):
    with debug.profile(5):
        pass
    assert "function calls" in capsys.readouterr().out


def test_timed(mocker):
    mocker.patch("vimiv.utils.log.info")
    expected = 42
    sleep_time_ms = 1

    @debug.timed
    def func():
        time.sleep(sleep_time_ms / 1000)
        return expected

    result = func()

    assert result == expected  # Ensure the result is preserved
    log.info.assert_called_once()  # Ensure a message was logged
    # Ensure the message contains the elapsed time
    message_args = log.info.call_args[0]
    message_time = message_args[-1]
    assert message_time == pytest.approx(sleep_time_ms, sleep_time_ms)
