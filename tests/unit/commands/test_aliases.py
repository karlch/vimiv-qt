# vim: ft=python fileencoding=utf-8 sw=4 et sts=4

# This file is part of vimiv.
# Copyright 2017-2020 Christian Karl (karlch) <karlch at protonmail dot com>
# License: GNU GPL v3, see the "LICENSE" and "AUTHORS" files for details.

"""Tests for vimiv.commands.aliases."""

import pytest

from vimiv import api
from vimiv.commands import aliases


def test_add_alias():
    aliases.alias("test", ["quit"])
    assert aliases.get(api.modes.GLOBAL)["test"] == "quit"
    del aliases._aliases[api.modes.GLOBAL]["test"]


def test_fail_add_alias_no_list():
    with pytest.raises(AssertionError, match="defined as list"):
        aliases.alias("test", "any")


def test_add_alias_for_different_mode():
    aliases.alias("test", ["quit"], mode="image")
    assert aliases.get(api.modes.IMAGE)["test"] == "quit"
    assert "test" not in aliases.get(api.modes.GLOBAL)
    del aliases._aliases[api.modes.IMAGE]["test"]


def test_get_global_alias_from_image_mode():
    assert "q" in aliases.get(api.modes.IMAGE)
