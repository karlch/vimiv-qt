# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2018 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.commands."""

from unittest.mock import Mock

from vimiv.commands import commands


def test_command_with_no_args(cleansetup):
    test = Mock()
    cmd = commands.Command("test", test)
    cmd([], None)
    test.assert_called_once()


def test_register_command(cleansetup):
    @commands.register()
    def test():
        pass
    assert "test" in commands.registry["global"]


def test_register_command_for_different_mode(cleansetup):
    @commands.register(mode="image")
    def test():
        pass
    assert "test" in commands.registry["image"]
