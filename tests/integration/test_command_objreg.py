# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests integration of vimiv.commands.commands with vimiv.utils.objreg."""

from unittest.mock import Mock

from vimiv.commands import commands, runners
from vimiv.utils import objreg


def test_run_cmd(mocker, cleansetup):
    class RunTest:
        """Simple class to register a command associated with an object."""

        @objreg.register("test")
        def __init__(self):
            self.mock = Mock()

        @commands.register(instance="test")
        def run(self):
            self.mock()

    runtest = RunTest()  # Register in objreg
    mocker.patch("vimiv.gui.statusbar.StatusBar.update")
    runner = runners.CommandRunner()
    runner("run", "image")
    runtest.mock.assert_called_once()
