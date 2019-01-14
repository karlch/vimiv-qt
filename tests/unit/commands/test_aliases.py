# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2019 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.aliases."""

import pytest

from vimiv import api
from vimiv.commands import aliases


def test_add_alias():
    aliases.alias("test", ["quit"])
    assert aliases.get(api.modes.GLOBAL)["test"] == "quit"


def test_fail_add_alias_no_list():
    with pytest.raises(AssertionError, match="defined as list"):
        aliases.alias("test2", "any")


def test_add_alias_for_different_mode():
    aliases.alias("test3", ["quit"], mode="image")
    assert aliases.get(api.modes.IMAGE)["test"] == "quit"
    assert "test3" not in aliases.get(api.modes.GLOBAL)


def test_get_global_alias_from_image_mode():
    assert "q" in aliases.get(api.modes.IMAGE)
