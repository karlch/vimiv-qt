# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.utils.xdg."""

import os

from vimiv.utils import xdg

import pytest


@pytest.fixture
def unset_xdg_env(monkeypatch):
    """Unset the XDG_*_HOME environment variables."""
    monkeypatch.delenv("XDG_CACHE_HOME", raising=False)
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)


@pytest.fixture
def mock_getenv(monkeypatch):
    """Mock getenv to always return '.'."""
    monkeypatch.setenv("XDG_CACHE_HOME", ".")
    monkeypatch.setenv("XDG_CONFIG_HOME", ".")
    monkeypatch.setenv("XDG_DATA_HOME", ".")


def test_xdg_defaults(unset_xdg_env):
    expected = {
        xdg.user_cache_dir: "~/.cache",
        xdg.user_config_dir: "~/.config",
        xdg.user_data_dir: "~/.local/share",
    }
    for func, expected_retval in expected.items():
        assert func() == os.path.expanduser(expected_retval)


def test_other_values(mock_getenv):
    for func in [xdg.user_cache_dir, xdg.user_config_dir, xdg.user_data_dir]:
        assert func() == "."


def test_vimiv_xdg_dirs(mock_getenv):
    for func in [xdg.vimiv_cache_dir, xdg.vimiv_config_dir, xdg.vimiv_data_dir]:
        assert func() == "./vimiv"


def test_join_vimiv_xdg_dirs(mock_getenv):
    for func in [xdg.vimiv_cache_dir, xdg.vimiv_config_dir, xdg.vimiv_data_dir]:
        assert func("pathname") == "./vimiv/pathname"


def test_join_vimiv_xdg_dirs_multiple_paths(mock_getenv):
    for func in [xdg.vimiv_cache_dir, xdg.vimiv_config_dir, xdg.vimiv_data_dir]:
        assert func("directory", "pathname") == "./vimiv/directory/pathname"
