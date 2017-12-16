# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests integration of vimiv.commands.commands with vimiv.utils.objreg."""

from unittest.mock import Mock

from vimiv.commands import commands
from vimiv.utils import objreg


class RunTest:
    """Simple class to register a command associated with an object."""

    @objreg.register("test")
    def __init__(self):
        self.mock = Mock()

    @commands.register(instance="test")
    def run(self):
        self.mock()


def test_run_cmd(mocker, objregistry):
    runtest = RunTest()  # Register
    mocker.patch("vimiv.gui.statusbar.StatusBar.update")
    commands.run("run")
    runtest.mock.assert_called_once()
