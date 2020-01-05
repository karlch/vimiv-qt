# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.plugins."""

import os

import pytest

from vimiv import plugins


@pytest.fixture
def mock_plugin(mocker):
    name = "mock_plugin"
    info = "useful"
    mocker.patch("mock_plugin.init")
    mocker.patch("mock_plugin.cleanup")
    plugins._load_plugin(name, info, os.path.abspath("."))
    plugins.cleanup()
    yield plugins._loaded_plugins[name], info
    del plugins._loaded_plugins[name]


def test_init_and_cleanup_plugin(mock_plugin):
    plugin, info = mock_plugin
    plugin.init.assert_called_once_with(info)
    plugin.cleanup.assert_called_once()


def test_do_not_fail_on_non_existing_plugin():
    plugins._load_plugin("does_not_exist", "any info", os.path.abspath("."))


def test_do_not_fail_on_plugin_with_syntax_error():
    name = "mock_plugin_syntax_error"
    info = "useful"
    plugins._load_plugin(name, info, os.path.abspath("."))
