# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.plugins."""

import os

import pytest

from vimiv import plugins


@pytest.fixture
def mock_plugin():
    name = "mock_plugin"
    plugins._load_plugin(name, os.path.abspath("."))
    plugins.cleanup()
    yield plugins._loaded_plugins[name]
    del plugins._loaded_plugins[name]


def test_init_and_cleanup_plugin(mock_plugin):
    mock_plugin.init.assert_called_once()
    mock_plugin.cleanup.assert_called_once()


def test_do_not_fail_on_non_existing_plugin():
    plugins._load_plugin("does_not_exist", os.path.abspath("."))
