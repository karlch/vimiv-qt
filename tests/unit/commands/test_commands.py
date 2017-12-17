# vim: ft=python fileencoding=utf-8 sw=4 et sts=4
"""Tests for vimiv.commands.commands."""

from unittest.mock import Mock

from vimiv.commands import commands


cmd_mock = Mock()


def test_run_with_no_args():
    @commands.register()
    def simple():
        cmd_mock.simple()
    commands.run("simple")
    cmd_mock.simple.assert_called_once()


def test_run_with_positional_argument():
    @commands.argument("arg")
    @commands.register()
    def pos_arg(arg):
        cmd_mock.pos_arg(arg)
    commands.run("pos-arg foo")
    cmd_mock.pos_arg.assert_called_once_with("foo")


def test_run_with_optional_argument():
    @commands.argument("arg", optional=True, default="default")
    @commands.register()
    def opt_arg(arg="default"):
        cmd_mock.opt_arg(arg=arg)
    commands.run("opt-arg")
    cmd_mock.opt_arg.assert_called_once_with(arg="default")
    commands.run("opt-arg --arg=foo")
    cmd_mock.opt_arg.assert_called_with(arg="foo")


def test_run_with_positional_and_optional_argument():
    @commands.argument("pos_arg")
    @commands.argument("opt_arg", optional=True, default="default")
    @commands.register()
    def both(pos_arg, opt_arg="default"):
        cmd_mock.both(pos_arg, opt_arg=opt_arg)
    commands.run("both baz")
    cmd_mock.both.assert_called_once_with("baz", opt_arg="default")
    commands.run("both bar --opt_arg=foo")
    cmd_mock.both.assert_called_with("bar", opt_arg="foo")


def test_run_command_with_different_mode():
    @commands.register(mode="image")
    def image():
        cmd_mock.image()
    commands.run("image", "image")
    cmd_mock.image.assert_called_once()
